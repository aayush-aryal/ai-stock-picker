"use client";

import { UserDTO } from "../definitions";
import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function NavBar(){
    const router=useRouter();
    const [user,setUser]=useState<UserDTO| null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
        router.push("/auth/login");
        return;
        }

        fetch("http://localhost:8000/auth/users/me", {
        headers: { Authorization: `Bearer ${token}` },
        })
        .then((res) => {
            if (!res.ok) {
            localStorage.removeItem("token");
            router.push("/auth/login");
            throw new Error("Unauthorized");
            }
            return res.json();
        })
        .then(setUser)
        .catch(console.error);
    }, [router]);


    return (
        <nav>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/news">Stock News</Link>
            <Link href="/earnings-call">Earnings Call</Link>
            <p>Current Capital {user?user.total_capital:'0'}</p>
        </nav>
    )
}