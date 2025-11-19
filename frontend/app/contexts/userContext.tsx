"use client";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import { UserDTO } from "../definitions";

const UserContext = createContext<{
  user: UserDTO | null;
  setUser: (u: UserDTO | null) => void;
}>({ user: null, setUser: () => {} });

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserDTO | null>(null);
  useEffect(() => {
    async function fetchUser() {
      const resp = await fetch("http://localhost:8000/auth/users/me", {
        credentials: "include",
      });
      console.log("resp", resp);
      if (!resp.ok) return;
      const user: UserDTO = await resp.json();
      setUser(user);
    }

    fetchUser();
  }, []);
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
