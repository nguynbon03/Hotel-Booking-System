"""
Pydantic schemas for Analytics and Reporting system.

These schemas define the structure for various analytics responses
including revenue, occupancy, booking patterns, and customer insights.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from decimal import Decimal
import uuid


# Base Analytics Schemas
class AnalyticsDateRange(BaseModel):
    """Date range for analytics queries."""
    start_date: date
    end_date: date


class MetricValue(BaseModel):
    """Generic metric with value and growth."""
    value: float
    growth_percentage: Optional[float] = None
    previous_value: Optional[float] = None


# Revenue Analytics
class RevenueAnalytics(BaseModel):
    """Comprehensive revenue analytics."""
    total_revenue: float = Field(..., description="Total revenue for the period")
    revenue_growth: float = Field(..., description="Revenue growth percentage vs previous period")
    average_booking_value: float = Field(..., description="Average value per booking")
    total_bookings: int = Field(..., description="Total number of bookings")
    confirmed_bookings: int = Field(..., description="Number of confirmed bookings")
    cancelled_bookings: int = Field(..., description="Number of cancelled bookings")
    cancellation_rate: float = Field(..., description="Cancellation rate percentage")
    revenue_by_day: Dict[str, float] = Field(..., description="Daily revenue breakdown")


class RevenueBreakdown(BaseModel):
    """Detailed revenue breakdown by various dimensions."""
    revenue_by_property: Dict[str, float] = Field(..., description="Revenue by property")
    revenue_by_room_type: Dict[str, float] = Field(..., description="Revenue by room type")
    revenue_by_month: Dict[str, float] = Field(..., description="Revenue by month")
    revenue_by_source: Dict[str, float] = Field(..., description="Revenue by booking source")


# Occupancy Analytics
class OccupancyAnalytics(BaseModel):
    """Occupancy rate and availability analytics."""
    overall_occupancy_rate: float = Field(..., description="Overall occupancy rate percentage")
    occupancy_by_day: Dict[str, float] = Field(..., description="Daily occupancy rates")
    total_rooms: int = Field(..., description="Total number of rooms")
    average_daily_rate: float = Field(..., description="Average daily rate (ADR)")
    revenue_per_available_room: float = Field(..., description="Revenue per available room (RevPAR)")


# Booking Analytics
class BookingAnalytics(BaseModel):
    """Booking patterns and conversion analytics."""
    total_bookings: int = Field(..., description="Total bookings in period")
    status_distribution: Dict[str, int] = Field(..., description="Bookings by status")
    bookings_by_weekday: Dict[int, int] = Field(..., description="Bookings by day of week (0=Monday)")
    average_lead_time: float = Field(..., description="Average days between booking and check-in")
    average_stay_length: float = Field(..., description="Average length of stay in days")
    conversion_rate: float = Field(..., description="Booking conversion rate percentage")
    repeat_customer_rate: float = Field(..., description="Percentage of repeat customers")


# Customer Analytics
class CustomerAnalytics(BaseModel):
    """Customer behavior and demographics analytics."""
    total_customers: int = Field(..., description="Total unique customers")
    new_customers: int = Field(..., description="New customers in period")
    repeat_customers: int = Field(..., description="Returning customers")
    repeat_customer_rate: float = Field(..., description="Repeat customer rate percentage")
    average_customer_value: float = Field(..., description="Average customer lifetime value")
    customer_segments: Dict[str, int] = Field(..., description="Customer segmentation")


# Property Performance
class PropertyPerformance(BaseModel):
    """Individual property performance metrics."""
    property_id: uuid.UUID
    property_name: str
    total_revenue: float
    total_bookings: int
    occupancy_rate: float
    average_daily_rate: float
    revenue_per_available_room: float
    customer_rating: Optional[float] = None
    total_rooms: int


# Top Performers
class TopPerformers(BaseModel):
    """Top performing entities across various metrics."""
    top_properties: List[Dict[str, Any]] = Field(..., description="Top properties by revenue")
    top_room_types: List[Dict[str, Any]] = Field(..., description="Top room types by bookings")
    top_customers: List[Dict[str, Any]] = Field(..., description="Top customers by value")
    best_performing_days: List[Dict[str, Any]] = Field(..., description="Best performing days")


# Analytics Summary
class AnalyticsSummary(BaseModel):
    """High-level analytics summary for dashboard."""
    total_revenue: float
    total_bookings: int
    total_properties: int
    total_rooms: int
    occupancy_rate: float
    average_daily_rate: float
    revenue_growth: float
    booking_growth: float


# Comparative Analytics
class ComparativeAnalytics(BaseModel):
    """Compare metrics across different periods."""
    current_period: AnalyticsSummary
    previous_period: AnalyticsSummary
    growth_metrics: Dict[str, float] = Field(..., description="Growth percentages for each metric")


# Forecast Analytics
class ForecastAnalytics(BaseModel):
    """Revenue and booking forecasts."""
    forecasted_revenue: Dict[str, float] = Field(..., description="Revenue forecast by month")
    forecasted_bookings: Dict[str, int] = Field(..., description="Booking forecast by month")
    confidence_interval: Dict[str, Dict[str, float]] = Field(..., description="Forecast confidence intervals")
    trend_analysis: str = Field(..., description="Trend analysis summary")


# Custom Report
class CustomReportRequest(BaseModel):
    """Request for custom analytics report."""
    report_name: str
    date_range: AnalyticsDateRange
    metrics: List[str] = Field(..., description="List of metrics to include")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    group_by: Optional[str] = Field(None, description="Group results by dimension")
    format: str = Field(default="json", description="Output format (json, csv, pdf)")


class CustomReportResponse(BaseModel):
    """Response for custom analytics report."""
    report_id: uuid.UUID
    report_name: str
    generated_at: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Real-time Analytics
class RealTimeMetrics(BaseModel):
    """Real-time metrics for live dashboard."""
    current_occupancy: float
    todays_revenue: float
    todays_bookings: int
    pending_check_ins: int
    pending_check_outs: int
    available_rooms: int
    last_updated: datetime


# Benchmark Analytics
class BenchmarkAnalytics(BaseModel):
    """Industry benchmark comparisons."""
    your_metrics: AnalyticsSummary
    industry_average: AnalyticsSummary
    percentile_ranking: Dict[str, float] = Field(..., description="Your ranking in each metric")
    recommendations: List[str] = Field(..., description="Improvement recommendations")


# Seasonal Analytics
class SeasonalAnalytics(BaseModel):
    """Seasonal trends and patterns."""
    monthly_trends: Dict[str, Dict[str, float]] = Field(..., description="Monthly patterns by metric")
    seasonal_factors: Dict[str, float] = Field(..., description="Seasonal adjustment factors")
    peak_seasons: List[Dict[str, Any]] = Field(..., description="Identified peak seasons")
    recommendations: List[str] = Field(..., description="Seasonal strategy recommendations")


# Channel Analytics
class ChannelAnalytics(BaseModel):
    """Booking channel performance analytics."""
    channel_performance: Dict[str, Dict[str, float]] = Field(..., description="Performance by channel")
    channel_costs: Dict[str, float] = Field(..., description="Cost per acquisition by channel")
    channel_conversion: Dict[str, float] = Field(..., description="Conversion rates by channel")
    roi_by_channel: Dict[str, float] = Field(..., description="ROI by marketing channel")


# Guest Satisfaction Analytics
class SatisfactionAnalytics(BaseModel):
    """Guest satisfaction and review analytics."""
    overall_rating: float
    rating_distribution: Dict[str, int] = Field(..., description="Distribution of ratings")
    satisfaction_trends: Dict[str, float] = Field(..., description="Satisfaction over time")
    common_complaints: List[Dict[str, Any]] = Field(..., description="Most common complaint categories")
    improvement_areas: List[str] = Field(..., description="Areas needing improvement")


# Financial Analytics
class FinancialAnalytics(BaseModel):
    """Detailed financial performance analytics."""
    gross_revenue: float
    net_revenue: float
    operating_expenses: float
    profit_margin: float
    cost_per_booking: float
    revenue_per_employee: float
    cash_flow_analysis: Dict[str, float]
    profitability_by_property: Dict[str, float]


# Export Schemas
class AnalyticsExportRequest(BaseModel):
    """Request to export analytics data."""
    report_type: str = Field(..., description="Type of report to export")
    date_range: AnalyticsDateRange
    format: str = Field(default="csv", description="Export format (csv, xlsx, pdf)")
    include_charts: bool = Field(default=False, description="Include charts in export")
    email_to: Optional[str] = Field(None, description="Email address to send export")


class AnalyticsExportResponse(BaseModel):
    """Response for analytics export."""
    export_id: uuid.UUID
    download_url: str
    expires_at: datetime
    file_size: int
    format: str
