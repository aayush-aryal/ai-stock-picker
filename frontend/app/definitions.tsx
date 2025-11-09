export type Token={
    "access_token":string,
    "token_type":string
}

export type RegisterUser={
    "username":string,
    "email":string,
    "password":string,
    "full_name":string,
}

export type UserDTO={
    "username":string,
    "full_name":string,
    "email":string,
    "total_capital":number
}