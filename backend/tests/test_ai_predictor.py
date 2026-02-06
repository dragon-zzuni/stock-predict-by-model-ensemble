"""AI 예측 모듈 테스트"""
import pytest
import json
from backend.ai_predictor.parser import ResponseParser
from backend.models.prediction import PeriodPrediction, ModelPrediction


class TestResponseParser:
    """ResponseParser 클래스 테스트"""
    
    def test_parse_valid_json_response(self):
        """유효한 JSON 응답 파싱 테스트"""
        response = {
            "success": True,
            "content": json.dumps({
                "1d": {"price": 50000, "reason": "단기 상승 예상", "sentiment": "긍정"},
                "1w": {"price": 52000, "reason": "주간 상승 추세", "sentiment": "긍정"},
                "1m": {"price": 55000, "reason": "월간 강세", "sentiment": "긍정"}
            })
        }
        
        result = ResponseParser.parse_response("TestModel", response)
        
        assert result is not None
        assert result.model_name == "TestModel"
        assert result.success is True
        assert "1d" in result.predictions
        assert "1w" in result.predictions
        assert "1m" in result.predictions
        assert result.predictions["1d"].price == 50000
        assert result.predictions["1d"].sentiment == "긍정"
    
    def test_parse_json_with_code_block(self):
        """코드 블록으로 감싸진 JSON 파싱 테스트"""
        response = {
            "success": True,
            "content": """
            여기 예측 결과입니다:
            ```json
            {
                "1d": {"price": 50000, "reason": "단기 상승", "sentiment": "긍정"},
                "1w": {"price": 52000, "reason": "주간 상승", "sentiment": "긍정"},
                "1m": {"price": 55000, "reason": "월간 강세", "sentiment": "긍정"}
            }
            ```
            """
        }
        
        result = ResponseParser.parse_response("TestModel", response)
        
        assert result is not None
        assert result.predictions["1d"].price == 50000
    
    def test_parse_invalid_response(self):
        """잘못된 응답 파싱 테스트"""
        response = {
            "success": True,
            "content": "이것은 JSON이 아닙니다"
        }
        
        result = ResponseParser.parse_response("TestModel", response)
        
        assert result is None
    
    def test_parse_missing_fields(self):
        """필수 필드 누락 응답 테스트"""
        response = {
            "success": True,
            "content": json.dumps({
                "1d": {"reason": "이유만 있음", "sentiment": "긍정"}
            })
        }
        
        result = ResponseParser.parse_response("TestModel", response)
        
        # 가격이 없으면 해당 기간 예측이 제외됨
        assert result is None or "1d" not in result.predictions
    
    def test_normalize_sentiment(self):
        """감성 정규화 테스트"""
        assert ResponseParser._normalize_sentiment("긍정") == "긍정"
        assert ResponseParser._normalize_sentiment("positive") == "긍정"
        assert ResponseParser._normalize_sentiment("bullish") == "긍정"
        assert ResponseParser._normalize_sentiment("부정") == "부정"
        assert ResponseParser._normalize_sentiment("negative") == "부정"
        assert ResponseParser._normalize_sentiment("bearish") == "부정"
        assert ResponseParser._normalize_sentiment("알 수 없음") == "중립"
    
    def test_parse_all_responses(self):
        """여러 모델 응답 일괄 파싱 테스트"""
        responses = {
            "Model1": {
                "success": True,
                "content": json.dumps({
                    "1d": {"price": 50000, "reason": "상승", "sentiment": "긍정"},
                    "1w": {"price": 52000, "reason": "상승", "sentiment": "긍정"},
                    "1m": {"price": 55000, "reason": "상승", "sentiment": "긍정"}
                })
            },
            "Model2": None,
            "Model3": {
                "success": True,
                "content": "잘못된 JSON"
            }
        }
        
        results = ResponseParser.parse_all_responses(responses)
        
        assert len(results) == 3
        assert results["Model1"] is not None
        assert results["Model2"] is None
        assert results["Model3"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
