import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, clearAuth, getStoredUser, getToken, setAuth } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);
  const [loading, setLoading] = useState(!!getToken());

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then((u) => {
        setUser(u);
        setAuth(token, u);
      })
      .catch(() => {
        clearAuth();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      async login(email, password) {
        const data = await api.login({ email, password });
        setAuth(data.access_token, data.user);
        setUser(data.user);
        return data.user;
      },
      async register(payload) {
        const data = await api.register(payload);
        setAuth(data.access_token, data.user);
        setUser(data.user);
        return data.user;
      },
      logout() {
        clearAuth();
        setUser(null);
      },
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
