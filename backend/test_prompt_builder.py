"""
PromptBuilder 동작 확인을 위한 테스트 스크립트
"""
from datetime import datetime
from backend.models.data import CollectedData, OHLCV
from backend.prompt_builder import PromptBuilder


def test_prompt_builder():
    """PromptBuilder 기본 동작 테스트"""
    
    # 테스트 데이터 생성
    test_data = CollectedData(
        symbol="035420.KQ",
        name="NAVER",
        current_price=250000,
        market_cap=41000000000000,
        trading_volume=500000,
        trading_value=125000000000,
        change_rate=2.5,
        historical_prices=[
            OHLCV(
                date=datetime(2024, 12, 30),
                open=245000,
                high=252000,
                low=244000,
                close=250000,
                volume=500000
            ),
            OHLCV(
                date=datetime(2024, 12, 29),
                open=240000,
                high=246000,
                low=239000,
                close=244000,
                volume=450000
            )
        ],
        technical_indicators={
            "MA20": 248000,
            "RSI": 65.5
        },
        news_summary="최근 AI 서비스 확장 발표로 긍정적 반응",
        sentiment_score=0.7,
        news_count=15
    )
    
    # PromptBuilder 생성
    builder = PromptBuilder()
    
    # 각 모델별 프롬프트 생성 테스트
    models = ["gpt", "gemini", "claude", "gemma", "qwen"]
    
    print("=" * 80)
    print("PromptBuilder 테스트 시작")
    print("=" * 80)
    
    for model in models:
        print(f"\n[{model.upper()} 모델 프롬프트]")
        print("-" * 80)
        prompt = builder.build_prompt(test_data, model)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print(f"\n프롬프트 길이: {len(prompt)}자")
        
        # 필수 요소 확인
        required_elements = [
            "종목 정보",
            "최근 시장 상황",
            "과거 추이",
            "기술적 지표",
            "뉴스 감성 분석",
            "1일 후",
            "1주일 후",
            "1개월 후",
            "JSON"
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in prompt]
        
        if missing_elements:
            print(f"⚠️  누락된 요소: {', '.join(missing_elements)}")
        else:
            print("✓ 모든 필수 요소 포함됨")
    
    # 전체 모델 프롬프트 일괄 생성 테스트
    print("\n" + "=" * 80)
    print("전체 모델 프롬프트 일괄 생성 테스트")
    print("=" * 80)
    
    all_prompts = builder.build_prompts_for_all_models(test_data)
    print(f"생성된 프롬프트 개수: {len(all_prompts)}")
    print(f"모델 목록: {', '.join(all_prompts.keys())}")
    
    # 모델별 차별화 확인
    print("\n" + "=" * 80)
    print("모델별 프롬프트 차별화 확인")
    print("=" * 80)
    
    unique_endings = set()
    for model, prompt in all_prompts.items():
        # 마지막 100자를 확인하여 차별화 여부 검증
        ending = prompt[-100:]
        unique_endings.add(ending)
        print(f"{model}: ...{ending}")
    
    if len(unique_endings) == len(all_prompts):
        print("\n✓ 모든 모델의 프롬프트가 차별화되어 있습니다")
    else:
        print(f"\n⚠️  일부 모델의 프롬프트가 동일합니다 (고유 개수: {len(unique_endings)})")
    
    print("\n" + "=" * 80)
    print("테스트 완료")
    print("=" * 80)


if __name__ == "__main__":
    test_prompt_builder()
