import os
import json
import requests
from dotenv import load_dotenv
import re

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"



# 정상구조: 입력 파싱 → 상태 저장 → 판단 → 계산 → 출력

# 1. imports
# 2. ** parse_korean_money
# 3. safe_json_loads
# 4. call_llm
# 5. decide_next_action
# 6. calculate_asset_plan
# 7. main


# =====================
# 2. 금액 전용 파서
# =====================

def parse_korean_money(text: str) -> int | None:
    text = text.replace(",", "").replace(" ", "")

    units = {
        "억": 100_000_000,
        "천만": 10_000_000,
        "백만": 1_000_000,
        "만": 10_000,
        "천": 1_000,
    }

    total = 0
    matched = False

    for unit, multiplier in units.items():
        match = re.search(rf"(\d+){unit}", text)
        if match:
            total += int(match.group(1)) * multiplier
            matched = True

    if matched:
        return total

    if text.isdigit():
        return int(text)

    return None

# 기간 전용 파서

def parse_period_input(text: str) -> int | None:
    text = text.replace(" ", "")

    total_months = 0
    matched = False

    match = re.search(r"(\d+)년", text)
    if match:
        total_months += int(match.group(1)) * 12
        matched = True

    match = re.search(r"(\d+)개월", text)
    if match:
        total_months += int(match.group(1))
        matched = True

    if matched:
        return total_months

    if text.isdigit():
        return int(text)

    return None



# =====================
# 비율 기반 자연어 파서
# =====================

def parse_relative_money(text: str, user_state: dict) -> int | None:
    text = text.replace(" ", "")

    # 기준 키워드 매핑
    base_map = {
        "월급": "monthly_income",
        "소득": "monthly_income",
        "급여": "monthly_income",
    }

    base_value = None
    for k, field in base_map.items():
        if k in text and field in user_state:
            base_value = user_state[field]
            break

    if base_value is None:
        return None

    # 퍼센트 표현 (30%, 30퍼)
    match = re.search(r"(\d+(?:\.\d+)?)\s*(%|퍼)", text)
    if match:
        ratio = float(match.group(1)) / 100
        return int(base_value * ratio)

    # 분수 표현 (1/3)
    match = re.search(r"(\d+)\s*/\s*(\d+)", text)
    if match:
        numerator = int(match.group(1))
        denominator = int(match.group(2))
        return int(base_value * (numerator / denominator))

    # 관용 표현
    if "절반" in text:
        return int(base_value * 0.5)

    if "3분의1" in text:
        return int(base_value / 3)

    return None

# 통합 파서
def parse_money_input(text: str, user_state: dict) -> int | None:
    # 1. 비율 기반 시도
    relative = parse_relative_money(text, user_state)
    if relative is not None:
        return relative

    # 2. 절대 금액 시도
    return parse_korean_money(text)



# =====================
# 3. SAFE JSON PARSER
# =====================
def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# =====================
# 4. LLM CALL
# =====================
def call_llm(messages, temperature=0.2):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]



# =====================
# 5. DECISION AGENT
# =====================
def decide_next_action(user_state: dict):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a decision-making agent.\n"
                "Respond ONLY in valid JSON.\n"
                "No explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                "현재 사용자 상태:\n"
                f"{json.dumps(user_state, ensure_ascii=False)}\n\n"
                "아래 형식으로만 응답해.\n"
                "{\n"
                '  "action": "ASK_MORE_INFO | CALCULATE | END",\n'
                '  "message": "string",\n'
                '  "required_fields": ["string"]\n'
                "}"
            ),
        },
    ]

    raw = call_llm(messages, temperature=0)
    parsed = safe_json_loads(raw)
    print(parsed)

    if not parsed:
        raise ValueError("Decision JSON parsing failed")

    return parsed


# =====================
# 6. CALCULATION AGENT
# =====================
def calculate_asset_plan(user_data: dict, max_retry=3):
    system_prompt = (
        "You are a Korean financial planner for young professionals.\n"
        "All explanations must be written in natural Korean.\n"
        "JSON keys must be written in English.\n"
        "All money values must be formatted as Korean won with comma separators.\n"
        "Example: \"400,000원\".\n"
        "Return ONLY valid JSON.\n\n"
        "Summary rules:\n"
        "- Start with: 현재 상황 기준으로 보면\n"
        "- Explain savings, emergency fund, ETF in words\n"
        "- Express time as 약 n년 n개월\n"
        "- Be realistic\n"
        "- Avoid financial jargon"
    )

    user_prompt = (
        "다음은 한국 사회초년생의 자산 정보이다.\n\n"
        "입력:\n"
        f"{json.dumps(user_data, ensure_ascii=False)}\n\n"
        "조건:\n"
        "- 월급 기준 현실적인 저축 가능 금액 산정\n"
        "- 비상금은 최소 생활비 6개월 기준\n"
        "- 저축 목표 달성까지 예상 개월 수 계산\n"
        "- ETF는 장기 투자로 설명\n\n"
        "출력 형식:\n"
        "{\n"
        '  "monthly_investable_amount": "string",\n'
        '  "monthly_breakdown": {\n'
        '    "savings": "string",\n'
        '    "etf": "string",\n'
        '    "emergency_fund": "string"\n'
        "  },\n"
        '  "time_to_goal_months": number,\n'
        '  "summary": "string"\n'
        "}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(max_retry):
        raw = call_llm(messages)
        parsed = safe_json_loads(raw)
        if parsed:
            return parsed

    raise ValueError("Calculation JSON parsing failed")


# =====================
# 7. MAIN
# =====================
if __name__ == "__main__":
    user_state = {
        "monthly_income": 3_000_000,
        "current_savings": 3_000_000,
    }

    while True:
        decision = decide_next_action(user_state)

        if decision["action"] == "ASK_MORE_INFO":
            input_failed = False

            for field in decision["required_fields"]:
                raw = input(f"{field} 값을 입력하세요: ")

                # 필드별 파서 분기
                if field in ["savings_period"]:
                    parsed = parse_period_input(raw)
                else:
                    parsed = parse_money_input(raw, user_state)

                if parsed is None:
                    print("입력을 이해하지 못했습니다. 다시 입력해주세요.")
                    input_failed = True
                    break

                user_state[field] = parsed

            # 하나라도 실패하면 상태 유지하고 다시 질문
            if input_failed:
                continue

        elif decision["action"] == "CALCULATE":
            result = calculate_asset_plan(user_state)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            break

        else:
            print("종료")
            break
