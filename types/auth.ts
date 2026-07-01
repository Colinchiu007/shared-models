// Module: auth -- Auto-generated from shared-models

export interface JWTPayload {
  user_id: number;
  username: string;
  role?: string;
  exp?: number | unknown;
}

export interface RefreshRequest {
  /** Refresh token */
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | unknown;
  token_type?: string;
  expires_in?: number;
  user_id?: number | unknown;
  username?: string | unknown;
  role?: string;
}

export interface UserLoginRequest {
  /** Username, email, or phone */
  account: string;
  password: string;
  login_method?: string;
}

export interface UserProfile {
  /** Internal user ID */
  user_id: number;
  /** Username */
  username: string;
  /** Display name */
  display_name?: string | unknown;
  /** Avatar URL */
  avatar_url?: string | unknown;
  /** Bio text */
  bio?: string | unknown;
  /** Personal website */
  website?: string | unknown;
  /** Company name */
  company?: string | unknown;
  /** Location */
  location?: string | unknown;
  /** Subscription plan */
  subscription_plan?: ("free", "basic", "pro");
  /** Daily video generation quota */
  video_quota?: number;
  /** Videos generated today */
  videos_used_today?: number;
  /** UI language preference */
  preferred_language?: string;
  /** TTS voice preference */
  preferred_voice?: string;
  /** Video aspect ratio */
  preferred_video_ratio?: string;
}

export interface UserRegisterRequest {
  username: string;
  email?: string | unknown;
  phone?: string | unknown;
  password: string;
  verify_code?: string | unknown;
}

export interface UserResponse {
  /** User UUID */
  id: string;
  /** Username */
  username: string;
  /** Email address */
  email: string;
  /** Subscription tier */
  subscription_type?: ("free", "basic", "pro", "enterprise");
  /** Registration date */
  created_at?: string | unknown;
  /** Account active status */
  is_active?: boolean;
}
