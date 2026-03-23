"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getMe } from "@/lib/api";

interface UserInfo {
  user_id: string;
  email: string;
  full_name?: string;
}

export default function AuthControls() {
  const [user, setUser] = useState<UserInfo | null>(null);

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("auth_token");
      if (!token) return;
      try {
        const me = await getMe();
        setUser(me);
      } catch {
        localStorage.removeItem("auth_token");
      }
    };
    init();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    setUser(null);
  };

  if (user) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <span>{user.full_name || user.email}</span>
        <button
          onClick={handleLogout}
          className="px-3 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3 text-xs">
      <Link
        href="/login"
        className="px-3 py-1 rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
      >
        Login
      </Link>
      <Link
        href="/register"
        className="px-3 py-1 rounded bg-primary-600 text-white hover:bg-primary-700"
      >
        Register
      </Link>
    </div>
  );
 }
