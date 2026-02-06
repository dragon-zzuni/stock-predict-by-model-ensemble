"""
AI 모델용 프롬프트 생성 클래스
"""
from typing import Dict
from models.data import CollectedData
import logging

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    수집된 데이터를 AI 모델용 프롬프트로 변환하는 클래스
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def __init__(self):
        """PromptBuilder 초기화"""
        self.base_template = self._create_base_template()
        self.model_adjustments = self._create_model_adjustments()
    
    def _create_base_template(self) -> str:
        """기본 프롬프트 템플릿 생성"""
        return """종목 정보:
- 종목명: {name}
- 종목 코드: {symbol}
- 현재가: {current_price:,.0f}원
- 시가총액: {market_cap:,.0f}원

최근 시장 상황:
- 등락률: {change_rate:+.2f}%
- 거래량: {trading_volume:,}주
- 거래대금: {trading_value:,.0f}원

과거 추이:
{historical_summary}

기술적 지표:
{technical_indicators}

뉴스 감성 분석:
{news_summary}

위 정보를 바탕으로 이 종목의 1일 후, 1주일 후, 1개월 후 주가를 예측하고,
각 예측에 대한 근거를 설명해주세요.

응답은 다음 JSON 형식으로 제공해주세요:
{{
  "1d": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1w": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1m": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}}
}}"""
    
    def _create_model_adjustments(self) -> Dict[str, str]:
        """모델별 프롬프트 조정 내용 생성"""
        return {
            "gpt": "\n\n정확한 JSON 형식으로만 응답해주세요. 추가 설명 없이 JSON만 반환하세요.",
            "gemini": "\n\n분석적이고 논리적인 근거를 제시해주세요. 데이터 기반의 객관적인 분석을 중시합니다.",
            "claude": "\n\n신중하고 균형잡힌 분석을 제공해주세요. 리스크 요인도 함께 고려해주세요.",
            "gemma": "\n\n간결하고 명확한 근거를 제시해주세요. JSON 형식을 정확히 지켜주세요.",
            "qwen": "\n\n시장 동향과 기술적 분석을 중심으로 예측해주세요. JSON 형식으로 응답하세요."
        }
    
    def build_prompt(self, data: CollectedData, model_type: str) -> str:
        """
        모델별 최적화된 프롬프트 생성
        
        Args:
            data: 수집된 종합 데이터
            model_type: AI 모델 타입 ("gpt", "gemini", "claude", "gemma", "qwen")
        
        Returns:
            생성된 프롬프트 문자열
        
        Requirements: 6.1, 6.2, 6.3, 6.4
        """
        # 과거 추이 요약 생성
        historical_summary = self._format_historical_summary(data)
        
        # 기술적 지표 포맷팅
        technical_indicators = self._format_technical_indicators(data)
        
        # 뉴스 감성 포맷팅
        news_summary = self._format_news_summary(data)
        
        # 기본 프롬프트 생성
        base_prompt = self.base_template.format(
            name=data.name,
            symbol=data.symbol,
            current_price=data.current_price,
            market_cap=data.market_cap,
            change_rate=data.change_rate,
            trading_volume=data.trading_volume,
            trading_value=data.trading_value,
            historical_summary=historical_summary,
            technical_indicators=technical_indicators,
            news_summary=news_summary
        )
        
        # 모델별 조정 추가
        model_adjustment = self.model_adjustments.get(model_type.lower(), "")
        final_prompt = base_prompt + model_adjustment
        
        logger.info(f"{model_type} 모델용 프롬프트 생성 완료 (길이: {len(final_prompt)}자)")
        
        return final_prompt
    
    def _format_historical_summary(self, data: CollectedData) -> str:
        """
        과거 데이터를 요약 문자열로 변환
        
        Args:
            data: 수집된 데이터
        
        Returns:
            과거 추이 요약 문자열
        """
        if not data.historical_prices:
            return "과거 데이터 없음"
        
        # 최근 데이터부터 정렬
        sorted_prices = sorted(data.historical_prices, key=lambda x: x.date, reverse=True)
        
        summary_lines = []
        
        # 최근 5일 데이터
        if len(sorted_prices) >= 5:
            recent_5d = sorted_prices[:5]
            avg_5d = sum(p.close for p in recent_5d) / len(recent_5d)
            summary_lines.append(f"- 최근 5일 평균: {avg_5d:,.0f}원")
        
        # 최근 20일 데이터
        if len(sorted_prices) >= 20:
            recent_20d = sorted_prices[:20]
            avg_20d = sum(p.close for p in recent_20d) / len(recent_20d)
            summary_lines.append(f"- 최근 20일 평균: {avg_20d:,.0f}원")
        
        # 최근 60일 데이터
        if len(sorted_prices) >= 60:
            recent_60d = sorted_prices[:60]
            avg_60d = sum(p.close for p in recent_60d) / len(recent_60d)
            summary_lines.append(f"- 최근 60일 평균: {avg_60d:,.0f}원")
        
        # 전체 기간 최고가/최저가
        if sorted_prices:
            max_price = max(p.high for p in sorted_prices)
            min_price = min(p.low for p in sorted_prices)
            summary_lines.append(f"- 기간 내 최고가: {max_price:,.0f}원")
            summary_lines.append(f"- 기간 내 최저가: {min_price:,.0f}원")
        
        return "\n".join(summary_lines) if summary_lines else "데이터 부족"
    
    def _format_technical_indicators(self, data: CollectedData) -> str:
        """
        기술적 지표를 문자열로 변환
        
        Args:
            data: 수집된 데이터
        
        Returns:
            기술적 지표 문자열
        """
        if not data.technical_indicators:
            return "기술적 지표 없음"
        
        indicator_lines = []
        for key, value in data.technical_indicators.items():
            indicator_lines.append(f"- {key}: {value:.2f}")
        
        return "\n".join(indicator_lines) if indicator_lines else "기술적 지표 없음"
    
    def _format_news_summary(self, data: CollectedData) -> str:
        """
        뉴스 감성 정보를 문자열로 변환
        
        Args:
            data: 수집된 데이터
        
        Returns:
            뉴스 감성 요약 문자열
        """
        if not data.news_summary and data.news_count == 0:
            return "최근 뉴스 없음"
        
        sentiment_label = "긍정적" if data.sentiment_score > 0 else "부정적" if data.sentiment_score < 0 else "중립적"
        
        lines = [
            f"- 최근 뉴스 개수: {data.news_count}개",
            f"- 전반적 감성: {sentiment_label} (점수: {data.sentiment_score:.2f})"
        ]
        
        if data.news_summary:
            lines.append(f"- 주요 내용: {data.news_summary}")
        
        return "\n".join(lines)
    
    def build_prompts_for_all_models(self, data: CollectedData) -> Dict[str, str]:
        """
        모든 AI 모델용 프롬프트를 한 번에 생성
        
        Args:
            data: 수집된 종합 데이터
        
        Returns:
            모델명을 키로 하는 프롬프트 딕셔너리
        """
        models = ["gpt", "gemini", "claude", "gemma", "qwen"]
        prompts = {}
        
        for model in models:
            prompts[model] = self.build_prompt(data, model)
        
        logger.info(f"총 {len(prompts)}개 모델용 프롬프트 생성 완료")
        
        return prompts
