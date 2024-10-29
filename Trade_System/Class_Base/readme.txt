这个库用于实现模拟交易逻辑

第一层：Context,包含一个总账户和交易日期数据（self.portfolio = Portfolio(self)）
第二层：Portfolio,主账户的主要作用在于统计资产和增删子账户，不涉及到交易层面
第三层：SubPortfolio，子账户涉及交易顶层和一系列的金钱转换  （未完全测试）
第四层：Position，仓位层面，设计交易操作命令   （未完全测试）
