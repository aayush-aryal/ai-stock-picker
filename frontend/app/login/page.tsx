"use client"

import { useState } from "react"
import { Token } from "../definitions"
import { useRouter } from "next/navigation"


export default function LoginPage(){
    const [email,setEmail]=useState("")
    const [password, setPassword]=useState("")
    const [error,setError]=useState("")
    const router=useRouter()

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
            console.log(data)
            window.localStorage.setItem("token",data.access_token)
            router.push('/dashboard')

        }catch(error){
            console.log(error)
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