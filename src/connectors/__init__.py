"""
Ad Platform API Connectors.

Unified interface for 12 major ad platforms with mock mode support.
"""

from src.connectors.base_connector import BaseAdConnector, ConnectorStatus
from src.connectors.google_ads_connector import GoogleAdsConnector
from src.connectors.meta_ads_connector import MetaAdsConnector
from src.connectors.campaign_manager_connector import CampaignManagerConnector
from src.connectors.dv360_connector import DV360Connector
from src.connectors.snapchat_ads_connector import SnapchatAdsConnector
from src.connectors.tiktok_ads_connector import TikTokAdsConnector
from src.connectors.twitter_ads_connector import TwitterAdsConnector
from src.connectors.linkedin_ads_connector import LinkedInAdsConnector
from src.connectors.tradedesk_connector import TradeDeskConnector
from src.connectors.amazon_dsp_connector import AmazonDSPConnector
from src.connectors.pinterest_ads_connector import PinterestAdsConnector
from src.connectors.apple_search_ads_connector import AppleSearchAdsConnector
from src.connectors.connector_manager import AdConnectorManager

__all__ = [
    "BaseAdConnector",
    "ConnectorStatus",
    # Phase 1: Core Platforms
    "GoogleAdsConnector",
    "MetaAdsConnector",
    "CampaignManagerConnector",
    "DV360Connector",
    # Phase 2: Additional Platforms
    "SnapchatAdsConnector",
    "TikTokAdsConnector",
    "TwitterAdsConnector",
    "LinkedInAdsConnector",
    "TradeDeskConnector",
    "AmazonDSPConnector",
    "PinterestAdsConnector",
    "AppleSearchAdsConnector",
    # Manager
    "AdConnectorManager",
]
