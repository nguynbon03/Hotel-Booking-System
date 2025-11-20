// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// User Types
export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  current_organization_id?: string;
}

export type UserRole = 'ADMIN' | 'STAFF' | 'CUSTOMER';

// Organization Types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  subscription_plan: SubscriptionPlan;
  created_at: string;
  updated_at: string;
}

export type SubscriptionPlan = 'FREE' | 'BASIC' | 'PROFESSIONAL' | 'ENTERPRISE';

// Property Types
export interface Property {
  id: string;
  name: string;
  description?: string;
  address: string;
  city: string;
  country: string;
  star_rating?: number;
  property_type: PropertyType;
  is_active: boolean;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export type PropertyType = 'HOTEL' | 'RESORT' | 'APARTMENT' | 'VILLA' | 'HOSTEL';

// Booking Types
export interface Booking {
  id: string;
  property_id: string;
  user_id: string;
  check_in_date: string;
  check_out_date: string;
  total_amount: number;
  status: BookingStatus;
  guest_count: number;
  created_at: string;
  updated_at: string;
}

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';

// Analytics Types
export interface AnalyticsData {
  revenue: RevenueAnalytics;
  occupancy: OccupancyAnalytics;
  bookings: BookingAnalytics;
  customers: CustomerAnalytics;
}

export interface RevenueAnalytics {
  total_revenue: number;
  monthly_revenue: number;
  revenue_growth: number;
  average_booking_value: number;
}

export interface OccupancyAnalytics {
  occupancy_rate: number;
  available_rooms: number;
  occupied_rooms: number;
  total_rooms: number;
}

export interface BookingAnalytics {
  total_bookings: number;
  pending_bookings: number;
  confirmed_bookings: number;
  cancelled_bookings: number;
}

export interface CustomerAnalytics {
  total_customers: number;
  new_customers: number;
  returning_customers: number;
  customer_satisfaction: number;
}
