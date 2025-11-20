import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Organization, LoginRequest, LoginResponse } from '@/types/api';
import { authService } from '@/services/authService';
import { apiClient } from '@/lib/api';
import { toast } from 'react-hot-toast';

// ============================================================
// 🔐 Auth Store Interface
// ============================================================

interface AuthState {
  // State
  user: User | null;
  currentOrganization: Organization | null;
  organizations: Organization[];
  isAuthenticated: boolean;
  isLoading: boolean;
  otpRequired: boolean;
  otpEmail: string;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  confirmOtp: (code: string) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
  getOrganizations: () => Promise<void>;
  switchOrganization: (orgId: string) => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
  clearAuth: () => void;
}

// ============================================================
// 🔐 Auth Store Implementation
// ============================================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial State
      user: null,
      currentOrganization: null,
      organizations: [],
      isAuthenticated: false,
      isLoading: false,
      otpRequired: false,
      otpEmail: '',

      // ============================================================
      // 🔑 Login Action
      // ============================================================
      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true });

          const response: LoginResponse = await apiClient.login(credentials);

          if (response.otp_required) {
            // OTP required - show OTP form
            set({
              otpRequired: true,
              otpEmail: response.email,
              isLoading: false,
            });
            toast.success('OTP code sent to your email');
          } else {
            // Direct login success
            const user = await apiClient.getCurrentUser();
            
            set({
              user,
              isAuthenticated: true,
              isLoading: false,
              otpRequired: false,
              otpEmail: '',
            });

            // Load organizations
            await get().getOrganizations();
            
            toast.success(`Welcome back, ${user.full_name}!`);
          }
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Login failed';
          toast.error(message);
          throw error;
        }
      },

      // ============================================================
      // 🔢 Confirm OTP Action
      // ============================================================
      confirmOtp: async (code: string) => {
        try {
          set({ isLoading: true });

          const { otpEmail } = get();
          const response = await apiClient.confirmLoginOtp({
            email: otpEmail,
            code,
          });

          const user = await apiClient.getCurrentUser();
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            otpRequired: false,
            otpEmail: '',
          });

          // Load organizations
          await get().getOrganizations();
          
          toast.success(`Welcome back, ${user.full_name}!`);
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Invalid OTP code';
          toast.error(message);
          throw error;
        }
      },

      // ============================================================
      // 🚪 Logout Action
      // ============================================================
      logout: async () => {
        console.log('🚪 Logout initiated...');
        try {
          await apiClient.logout();
          console.log('✅ API logout successful');
        } catch (error) {
          console.log('⚠️ API logout error (ignored):', error);
        } finally {
          console.log('🧹 Clearing auth state...');
          set({
            user: null,
            currentOrganization: null,
            organizations: [],
            isAuthenticated: false,
            otpRequired: false,
            otpEmail: '',
          });
          toast.success('Logged out successfully');
          console.log('✅ Logout completed');
        }
      },

      // ============================================================
      // 👤 Get Current User Action
      // ============================================================
      getCurrentUser: async () => {
        try {
          if (!apiClient.isAuthenticated()) {
            return;
          }

          const user = await apiClient.getCurrentUser();
          set({ user, isAuthenticated: true });

          // Load organizations if user has current_organization_id
          if (user.current_organization_id) {
            await get().getOrganizations();
          }
        } catch (error: any) {
          if (error.response?.status === 401) {
            get().clearAuth();
          }
        }
      },

      // ============================================================
      // 🏢 Get Organizations Action
      // ============================================================
      getOrganizations: async () => {
        try {
          const organizations = await apiClient.getOrganizations();
          const { user } = get();
          
          // Find current organization
          let currentOrganization = null;
          if (user?.current_organization_id) {
            currentOrganization = organizations.find(
              (org: Organization) => org.id === user.current_organization_id
            ) || null;
          }

          set({
            organizations,
            currentOrganization,
          });
        } catch (error: any) {
          console.error('Failed to load organizations:', error);
        }
      },

      // ============================================================
      // 🔄 Switch Organization Action
      // ============================================================
      switchOrganization: async (orgId: string) => {
        try {
          set({ isLoading: true });

          await apiClient.switchOrganization(orgId);
          
          // Update user's current organization
          const updatedUser = await apiClient.getCurrentUser();
          const { organizations } = get();
          
          const newCurrentOrg = organizations.find(org => org.id === orgId) || null;
          
          set({
            user: updatedUser,
            currentOrganization: newCurrentOrg,
            isLoading: false,
          });

          toast.success(`Switched to ${newCurrentOrg?.name || 'organization'}`);
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Failed to switch organization';
          toast.error(message);
          throw error;
        }
      },

      // ============================================================
      // 📝 Update User Action
      // ============================================================
      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({
            user: { ...user, ...userData },
          });
        }
      },

      // ============================================================
      // 🧹 Clear Auth Action
      // ============================================================
      clearAuth: () => {
        set({
          user: null,
          currentOrganization: null,
          organizations: [],
          isAuthenticated: false,
          otpRequired: false,
          otpEmail: '',
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        currentOrganization: state.currentOrganization,
        organizations: state.organizations,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// ============================================================
// 🔧 Auth Utilities
// ============================================================

export const useAuth = () => {
  const authStore = useAuthStore();
  
  return {
    ...authStore,
    hasRole: (role: string) => authStore.user?.role === role,
    hasAnyRole: (roles: string[]) => roles.includes(authStore.user?.role || ''),
    isAdmin: () => authStore.user?.role === 'ADMIN',
    isStaff: () => authStore.user?.role === 'STAFF' || authStore.user?.role === 'ADMIN',
    isCustomer: () => authStore.user?.role === 'CUSTOMER',
  };
};

// ============================================================
// 🔐 Auth Guards
// ============================================================

export const requireAuth = () => {
  const { isAuthenticated, user } = useAuthStore();
  
  if (!isAuthenticated || !user) {
    throw new Error('Authentication required');
  }
  
  return user;
};

export const requireRole = (requiredRole: string) => {
  const user = requireAuth();
  
  if (user.role !== requiredRole) {
    throw new Error(`Role ${requiredRole} required`);
  }
  
  return user;
};

export const requireAnyRole = (requiredRoles: string[]) => {
  const user = requireAuth();
  
  if (!requiredRoles.includes(user.role)) {
    throw new Error(`One of roles ${requiredRoles.join(', ')} required`);
  }
  
  return user;
};
