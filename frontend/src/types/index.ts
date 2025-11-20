// ============================================================
// 🔐 Authentication Types
// ============================================================

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  current_organization_id?: string;
  avatar_url?: string;
  timezone: string;
  language: string;
  last_login_at?: string;
  is_verified: boolean;
  is_suspended: boolean;
  suspended_reason?: string;
  suspended_until?: string;
}

export enum UserRole {
  CUSTOMER = 'CUSTOMER',
  ADMIN = 'ADMIN',
  STAFF = 'STAFF',
}

export enum OrganizationRole {
  OWNER = 'OWNER',
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  STAFF = 'STAFF',
  MEMBER = 'MEMBER',
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  otp_required: boolean;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  role: UserRole;
  full_name: string;
  email: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  role: UserRole;
  full_name: string;
  email: string;
}

// ============================================================
// 🏢 Organization Types
// ============================================================

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  contact_email: string;
  contact_phone?: string;
  website?: string;
  address?: string;
  city?: string;
  country?: string;
  subscription_plan: SubscriptionPlan;
  status: OrganizationStatus;
  max_properties: number;
  max_users: number;
  max_rooms_per_property: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  trial_ends_at?: string;
  subscription_ends_at?: string;
  primary_color?: string;
  secondary_color?: string;
  logo_url?: string;
}

export enum SubscriptionPlan {
  FREE = 'FREE',
  BASIC = 'BASIC',
  PROFESSIONAL = 'PROFESSIONAL',
  ENTERPRISE = 'ENTERPRISE',
}

export enum OrganizationStatus {
  ACTIVE = 'ACTIVE',
  SUSPENDED = 'SUSPENDED',
  TRIAL = 'TRIAL',
  EXPIRED = 'EXPIRED',
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  role: OrganizationRole;
  can_manage_properties: boolean;
  can_manage_bookings: boolean;
  can_manage_users: boolean;
  can_view_analytics: boolean;
  can_manage_billing: boolean;
  is_active: boolean;
  invited_at: string;
  joined_at?: string;
}

// ============================================================
// 🏨 Property & Room Types
// ============================================================

export interface Property {
  id: string;
  name: string;
  location?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  organization_id: string;
  owner_id?: string;
  property_type: string;
  star_rating?: number;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  city?: string;
  country?: string;
  postal_code?: string;
  latitude?: number;
  longitude?: number;
  check_in_time: string;
  check_out_time: string;
  currency: string;
  cancellation_policy?: string;
  house_rules?: string;
  main_image_url?: string;
  updated_at: string;
}

export interface Room {
  id: string;
  number: string;
  type: string;
  room_type_id?: string;
  property_id?: string;
  price_per_night: number;
  capacity: number;
  description?: string;
  image_url?: string;
  is_active: boolean;
  created_at: string;
}

export interface RoomType {
  id: string;
  property_id: string;
  name: string;
  max_occupancy: number;
  description?: string;
  is_active: boolean;
}

// ============================================================
// 📅 Booking Types
// ============================================================

export interface Booking {
  id: string;
  user_id?: string;
  room_id: string;
  property_id?: string;
  room_type_id?: string;
  rate_plan_id?: string;
  check_in: string;
  check_out: string;
  total_amount: number;
  status: BookingStatus;
  created_at: string;
  updated_at: string;
}

export enum BookingStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  CANCELLED = 'CANCELLED',
  NO_SHOW = 'NO_SHOW',
  COMPLETED = 'COMPLETED',
}

// ============================================================
// 💳 Payment Types
// ============================================================

export interface Payment {
  id: string;
  booking_id: string;
  amount: number;
  method: string;
  status: string;
  transaction_code: string;
  created_at: string;
}

// ============================================================
// 📊 Analytics Types
// ============================================================

export interface RevenueAnalytics {
  total_revenue: number;
  revenue_growth: number;
  average_booking_value: number;
  total_bookings: number;
  confirmed_bookings: number;
  cancelled_bookings: number;
  cancellation_rate: number;
  revenue_by_day: Record<string, number>;
}

export interface OccupancyAnalytics {
  overall_occupancy_rate: number;
  occupancy_by_day: Record<string, number>;
  total_rooms: number;
  average_daily_rate: number;
  revenue_per_available_room: number;
}

export interface BookingAnalytics {
  total_bookings: number;
  status_distribution: Record<string, number>;
  bookings_by_weekday: Record<number, number>;
  average_lead_time: number;
  average_stay_length: number;
  conversion_rate: number;
  repeat_customer_rate: number;
}

export interface CustomerAnalytics {
  total_customers: number;
  new_customers: number;
  repeat_customers: number;
  repeat_customer_rate: number;
  average_customer_value: number;
  customer_segments: Record<string, number>;
}

export interface AnalyticsSummary {
  total_revenue: number;
  total_bookings: number;
  total_properties: number;
  total_rooms: number;
  occupancy_rate: number;
  average_daily_rate: number;
  revenue_growth: number;
  booking_growth: number;
}

// ============================================================
// 🔧 Utility Types
// ============================================================

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

// ============================================================
// 🎨 UI Types
// ============================================================

export interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  path: string;
  badge?: string | number;
  children?: MenuItem[];
  permissions?: string[];
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
  width?: string;
}

export interface FilterOption {
  key: string;
  label: string;
  type: 'select' | 'date' | 'text' | 'number';
  options?: SelectOption[];
  placeholder?: string;
}

// ============================================================
// 📱 Dashboard Types
// ============================================================

export interface DashboardStats {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon: React.ComponentType<any>;
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

export interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}
