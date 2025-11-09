"use client"

import { useState } from "react"
import { Token } from "../definitions"
import {redirect} from "next/navigation"

export default function LoginPage(){
    const [email,setEmail]=useState("")
    const [password, setPassword]=useState("")
    const [error,setError]=useState("")

    async function handleSubmit(e:React.FormEvent){
        e.preventDefault()
        setError("")

        try{
            const res=await fetch("http://localhost:8000/auth/token",{
                method:"POST",
                headers:{
                    "Content-Type":"application/x-www-form-urlencoded",
                },
                body:new URLSearchParams({"username":email,"password":password})
            });
            if (!res.ok){
                setError("Invalid Credentials")
                return; 
            }
            const data:Token=await res.json()
            window.localStorage.setItem("token",data.access_token)
            redirect("/dashboard")

        }catch{
            setError("Something went wrong when logging in")
        }
    }
    return (
        <div>
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <input
                placeholder="username"
                name="username"
                value={email}
                onChange={(e)=>setEmail(e.target.value)} />

                 <input type="password" 
                 placeholder="Password"
                 name="password"
                 value={password}
                 onChange={(e)=> setPassword(e.target.value)}/>
                 <button type="submit">Login</button>
                 <p>{error}</p>
            </form>
        </div>
    )
}