

if __name__ == "__main__":

    from model.df import FundParamDF, FundTypeParamDF
    # df = FundParamDF().df
    #print(df.head(100))
    df = FundTypeParamDF().df
    print(df)
