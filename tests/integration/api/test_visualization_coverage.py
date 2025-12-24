
import pytest
from fastapi import status

class TestVisualizationCoverage:
    """Tests for Visualization endpoints."""

    def test_recommend_chart_logic(self, client, auth_token):
        """Test chart recommendation logic."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test Case 1: Time Series -> Line
        payload_time = {
            "data_summary": {
                "has_time": True,
                "metrics": 1,
                "dimensions": 1
            },
            "intent": "trend"
        }
        resp = client.post("/api/v1/visualizations/recommend", json=payload_time, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["recommended"]["chart_type"] == "line"

        # Test Case 2: Comparison -> Bar
        payload_cat = {
            "data_summary": {
                "has_time": False,
                "metrics": 1,
                "dimensions": 1
            }
        }
        resp = client.post("/api/v1/visualizations/recommend", json=payload_cat, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["recommended"]["chart_type"] in ["bar", "pie", "radar"]

    def test_get_visualization_data(self, client, auth_token):
        """Test data retrieval for charts."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "metric": "spend",
            "dimension": "platform"
        }
        
        resp = client.post("/api/v1/visualizations/data", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "chart_data" in data
        assert len(data["chart_data"]) > 0

    def test_sankey_data(self, client, auth_token):
        """Test Sankey diagram data."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "source_layer": "channel",
            "target_layer": "conversion"
        }
        
        resp = client.post("/api/v1/visualizations/sankey", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "nodes" in data
        assert "links" in data

    def test_color_palettes(self, client):
        """Test public palette endpoint."""
        resp = client.get("/api/v1/visualizations/palettes")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3
