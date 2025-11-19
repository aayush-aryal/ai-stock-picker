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

export type StockDaysData={
    ticker:string;
    data:StockData[]
}

export type StockData={
    Date:string;
    Close:number;
}


export type NewsResponse={
    uuid:string;
    related_symbols:Array<string>;
    title:string;
    publisher:string;
    report_date:string;
    type:string;
    link:string;
    news:NewsParagraph[]
}

export type NewsParagraph={
    paragraph_number:number;
    highlight:string;
    paragraph:string;
}


export type RagRequest={
    ticker:string;
    query:string;
    quarter?:string;
    year?:string;
}