"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { api, authEvents } from "./api";

interface User {
  id: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (apiKey: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/** Routes that require an authenticated session. */
const PROTECTED_PREFIXES = ["/dashboard"];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const isProtectedRoute = (path: string) =>
    PROTECTED_PREFIXES.some(
      (prefix) => path === prefix || path.startsWith(`${prefix}/`)
    );

  const logout = useCallback(() => {
    sessionStorage.removeItem("aegis_api_key");
    setUser(null);
    router.push("/login");
  }, [router]);

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };

    authEvents.addEventListener("unauthorized", handleUnauthorized);
    return () => authEvents.removeEventListener("unauthorized", handleUnauthorized);
  }, [logout]);

  useEffect(() => {
    const initAuth = async () => {
      const token = sessionStorage.getItem("aegis_api_key");
      if (!token) {
        setLoading(false);
        if (isProtectedRoute(pathname)) {
          router.push("/login");
        }
        return;
      }

      try {
        // Fetch a protected endpoint to validate the token
        await api.get("/api/v1/policies");

        // For now, mock the user context based on success.
        // In a real app we'd decode a JWT or hit a /me endpoint.
        setUser({
          id: "current-user",
          name: "Aegis Admin",
          role: "ADMIN",
        });
      } catch (error) {
        console.error("Auth init failed:", error);
        sessionStorage.removeItem("aegis_api_key");
        if (isProtectedRoute(pathname)) {
          router.push("/login");
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [pathname, router]);

  const login = async (apiKey: string) => {
    sessionStorage.setItem("aegis_api_key", apiKey);
    try {
      // Validate key by making a request
      await api.get("/api/v1/policies");
      setUser({
        id: "current-user",
        name: "Aegis Admin",
        role: "ADMIN",
      });
      router.push("/dashboard");
    } catch (error) {
      sessionStorage.removeItem("aegis_api_key");
      throw error;
    }
  };


  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
