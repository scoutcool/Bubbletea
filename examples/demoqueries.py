query = {
    "sushiexchange"  : """
        {
            pairDayDatas(
                where:{date_gte:1628337600, date_lt:1628977289}
                orderBy: date
                orderDirection: asc
                bypassPagination: true
            ) {
                id
                date
                token0{
                symbol
                decimals
                }
                token1{
                symbol
                decimals
                }
                volumeUSD
            }
        }""",

    "sushibar"       : """""",

    "aave"           : """
        {
            deposits(
                where:{timestamp_gte:1628337600, timestamp_lt:1628977289}
                orderBy: timestamp
                orderDirection: asc
                bypassPagination: true
            ) {
                reserve {
                    symbol,
                    decimals
                }
                amount
                timestamp
            }
        }"""
}


