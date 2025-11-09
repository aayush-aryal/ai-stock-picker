"use client"
import { useState } from "react"
import { RegisterUser } from "../definitions";
import { redirect } from "next/navigation";
export default function RegisterPage(){
    const [username,setUsername]=useState("");
    const [password,setPassword]=useState("")
    const [confirmpassword,setConfirmPassword]=useState("")
    const [error,setError]=useState("")
    const [email,setEmail]=useState("")

    async function handleSubmit(e:React.FormEvent){
        e.preventDefault();
        setError("")
        //confirm if password and confirm password are 
        if (confirmpassword!==password){
            setError("Password and Confirm Password must be equal")
            return;
        }
        const registerUserRequest:RegisterUser={
            "username":username,
            "email":email,
            "password":password,
            "full_name":username
        }
        const resp= await fetch("http://localhost:8000/auth/users/register",
            {
                "method":"POST",
                "headers":{
                    "Content-Type":"application/json",
                },
                "body":JSON.stringify(registerUserRequest)
            }
        )
        if (!resp.ok){
            setError("Something went wrong... :( sowwy")
            return;
        }
        setError("Registration successfull!")
        await new Promise((resolve) => setTimeout(resolve, 1000));
        redirect("/login")
    }
    return (
        <div>
        <h1>Register</h1>
            <form onSubmit={handleSubmit}>
                <input 
                    type="text"
                    name="username"
                    value={username}
                    placeholder="username"
                    onChange={(e)=>setUsername(e.target.value)}
                 />
                <input 
                    type="email"
                    name="email"
                    value={email}
                    placeholder="email"
                    onChange={(e)=>setEmail(e.target.value)}
                 />
                 <input
                    type="password"
                    name="password"
                    value={password}
                    placeholder="password"
                    onChange={(e)=>setPassword(e.target.value)}
                 />
                <input
                    type="password"
                    name="confirm_password"
                    value={confirmpassword}
                    placeholder="password"
                    onChange={(e)=>setConfirmPassword(e.target.value)}
                 />
                 <p>{error}</p>
                 <button type="submit">Register</button>
            </form>
        </div>
    )
}