"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useUser } from "../contexts/userContext"


export default function LoginPage(){
    const [email,setEmail]=useState("")
    const [password, setPassword]=useState("")
    const [error,setError]=useState("")
    const router=useRouter()
    const {setUser}=useUser();

    async function handleSubmit(e:React.FormEvent){
        e.preventDefault()
        setError("")

        try{
            const res=await fetch("http://localhost:8000/auth/token",{
                method:"POST",
                headers:{
                    "Content-Type":"application/x-www-form-urlencoded",
                },
                credentials:"include",
                body:new URLSearchParams({"username":email,"password":password})
            });
            if (!res.ok){
                setError("Invalid Credentials")
                return; 
            }
            const user_res=await fetch("http://localhost:8000/auth/users/me", {"credentials":"include"})
            console.log("after logging in", user_res)
            if (user_res.ok){
                const user= await user_res.json()
                setUser(user);
            }
            router.push('/dashboard')

        }catch(error){
            setError("Something went wrong when logging in")
        }
    }
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
                <h1 className="text-4xl font-bold mb-6 text-center">Stockopedia</h1>
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <input
                    type="text"
                    placeholder="Username"
                    name="username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <input
                    type="password"
                    placeholder="Password"
                    name="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <button
                    type="submit"
                    className="w-full p-3 bg-indigo-500 text-white font-semibold rounded-md hover:bg-indigo-600 transition"
                >
                    Login
                </button>
                <p className="text-red-500 text-sm mt-2">{error}</p>
                </form>
            </div>
        </div>    
    )
}