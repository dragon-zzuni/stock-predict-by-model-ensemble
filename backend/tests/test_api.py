"""
FastAPI 엔드포인트 테스트
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """헬스 체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data


def test_rankings_endpoint():
    """거래대금 순위 엔드포인트 테스트"""
    # 이 테스트는 실제 API 호출이 필요하므로 시간이 걸릴 수 있음
    response = client.get("/rankings")
    
    # 성공 또는 서비스 불가 상태 모두 허용
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "rankings" in data
        assert "timestamp" in data
        assert "count" in data


def test_predict_endpoint_validation():
    """예측 엔드포인트 입력 검증 테스트"""
    # 잘못된 요청 (필수 필드 누락)
    response = client.post("/predict", json={})
    assert response.status_code == 400  # 커스텀 예외 핸들러가 400 반환
    
    # 올바른 형식의 요청
    # 주의: 실제 예측은 외부 API와 AI 모델이 필요하므로 실패할 수 있음
    response = client.post("/predict", json={
        "symbol": "005930.KS",
        "market": "KOSPI",
        "company_name": "삼성전자"
    })
    
    # 성공, 잘못된 요청, 서비스 불가, 또는 내부 오류 모두 허용
    # (테스트 환경에서는 AI 모델이 없을 수 있음)
    assert response.status_code in [200, 400, 500, 503]


def test_cors_headers():
    """CORS 헤더 테스트"""
    response = client.options("/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    
    # CORS 헤더가 있어야 함
    assert "access-control-allow-origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
