/**
 * Authentication API calls
 */

const API_BASE_URL = 'http://localhost:8000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignUpData {
  name: string;
  email: string;
  password: string;
  password_confirm: string;
  age?: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  age: number | null;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export class AuthAPI {
  static async signup(data: SignUpData): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  }

  static async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  static async getCurrentUser(token: string): Promise<User> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }

      return await response.json();
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  static async validateToken(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      return response.ok;
    } catch {
      return false;
    }
  }

  // Storage helpers
  static saveToken(token: string): void {
    localStorage.setItem('authToken', token);
  }

  static getToken(): string | null {
    return localStorage.getItem('authToken');
  }

  static removeToken(): void {
    localStorage.removeItem('authToken');
  }

  static saveUser(user: User): void {
    localStorage.setItem('currentUser', JSON.stringify(user));
  }

  static getUser(): User | null {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
  }

  static removeUser(): void {
    localStorage.removeItem('currentUser');
  }

  static logout(): void {
    this.removeToken();
    this.removeUser();
  }
}
