from tabulate import tabulate


def get_global_income_tax(dividend_income, annual_salary):
    """
    금융 소득까지 합산된 종합소득산출세액 계산
    """
    gross_up = (dividend_income - 20000000) * 0.11
    # Gross-up 한 금융소득금액
    financial_income = dividend_income + gross_up
    total_income = financial_income + annual_salary
    # 종합소득세
    tax_first = calc_separate_taxation(total_income)
    tax_second = (
        calc_global_income_tax(total_income - financial_income) + dividend_income * 0.14
    )
    global_income_tax_before_credit = max(tax_first, tax_second)
    # 배당세액공제액
    tax_credit_limit = calc_tax_credit_for_dividend_limit(
        dividend_income, annual_salary, total_income
    )
    tax_credit_for_dividend = min(gross_up, tax_credit_limit)
    return int(global_income_tax_before_credit - tax_credit_for_dividend)


def calc_separate_taxation(income):
    """
    금융소득 2천만원 까지는 14% 세율로 분리과세(지방소득세는 별도)
    """
    return calc_global_income_tax(income - 20000000) + 20000000 * 0.14


def calc_global_income_tax(amount):
    """
    과세표준에 따른 종합소득세 계산(2023년도 버전)
    """
    if amount <= 12000000:
        global_income_tax = amount * 0.06
    elif amount <= 46000000:
        global_income_tax = amount * 0.15 - 1080000
    elif amount <= 88000000:
        global_income_tax = amount * 0.24 - 5220000
    elif amount <= 150000000:
        global_income_tax = amount * 0.35 - 14900000
    elif amount <= 300000000:
        global_income_tax = amount * 0.38 - 19400000
    elif amount <= 500000000:
        global_income_tax = amount * 0.40 - 25400000
    elif amount <= 1000000000:
        global_income_tax = amount * 0.42 - 35400000
    else:
        global_income_tax = amount * 0.45 - 65400000
    return int(global_income_tax)


def calc_corporation_tax(amount):
    """
    과세표준에 따른 법인세 계산
    청년창업기업 세액감면은 미적용
    """
    if amount <= 500000000:
        corporation_tax = amount * 0.1
    elif amount <= 20000000000:
        corporation_tax = amount * 0.2 - 50000000
    else:
        corporation_tax = amount * 0.22 - 440000000
    return int(corporation_tax)


def calc_local_income_tax(global_income_tax):
    """
    지방소득세 계산(종합소득세분, 법인세분)
    """
    return int(global_income_tax * 0.1)


def get_annual_salary(gross_profit):
    """
    세전 연봉 산출
    """
    return 50000000


def calc_tax_credit_for_dividend_limit(dividend_income, annual_salary, total_income):
    """
    배당세액공제 한도액
    """
    limit_first = calc_separate_taxation(total_income)
    limit_second = dividend_income * 0.14 + calc_global_income_tax(annual_salary)
    return max(limit_first, limit_second) - limit_second


def get_sole_proprietorship_tax(gross_profit):
    global_income_tax = calc_global_income_tax(gross_profit)
    local_income_tax = calc_local_income_tax(global_income_tax)
    income_after_tax = gross_profit - global_income_tax - local_income_tax
    return {
        "net_income": gross_profit,  # 순이익 = 매출총이익 가정
        "global_income_tax": global_income_tax,
        "local_income_tax": local_income_tax,
        "income_after_tax": income_after_tax,
    }


def get_corporation_tax(gross_profit):
    annual_salary = get_annual_salary(gross_profit)
    net_income = gross_profit - annual_salary
    corporation_tax = calc_corporation_tax(net_income)
    local_income_tax_corp = calc_local_income_tax(corporation_tax)
    # 배당금 계산
    dividend_income = net_income - corporation_tax - local_income_tax_corp

    # 종합소득세 계산
    global_income_tax = get_global_income_tax(dividend_income, annual_salary)
    local_income_tax_global = calc_local_income_tax(global_income_tax)
    income_after_tax = (
        dividend_income + annual_salary - global_income_tax - local_income_tax_global
    )
    return {
        "dividend_income": dividend_income,
        "net_income": net_income,
        "gross_profit": gross_profit,
        "annual_salary": annual_salary,
        "corporation_tax": corporation_tax,
        "local_income_tax_corp": local_income_tax_corp,
        "global_income_tax": global_income_tax,
        "local_income_tax_global": local_income_tax_global,
        "income_after_tax": income_after_tax,
    }


def display_results(sole_tax_results, corp_tax_results):
    data = [
        ["순이익", f"{sole_tax_results['net_income']:,}"],
        ["종합소득세", f"({sole_tax_results['global_income_tax']:,})"],
        ["지방소득세", f"({sole_tax_results['local_income_tax']:,})"],
        [
            "세후소득",
            f"{sole_tax_results['income_after_tax']:,}",
            f"{corp_tax_results['income_after_tax']:,}",
        ],
    ]
    print("\n")
    print(tabulate(data, headers=["항목(개인사업자)", "금액(원)"], colalign=("left", "right")))

    data = [
        ["배당금", f"{corp_tax_results['dividend_income']:,}"],
        ["..순이익", f"{corp_tax_results['net_income']:,}"],
        ["....매출총이익", f"{corp_tax_results['gross_profit']:,}"],
        ["....판매비와관리비(급여)", f"({corp_tax_results['annual_salary']:,})"],
        ["..법인세", f"({corp_tax_results['corporation_tax']:,})"],
        ["..지방소득세(법인세분)", f"({corp_tax_results['local_income_tax_corp']:,})"],
        ["급여", f"{corp_tax_results['annual_salary']:,}"],
        ["종합소득세", f"({corp_tax_results['global_income_tax']:,})"],
        ["지방소득세(종합소득세분)", f"({corp_tax_results['local_income_tax_global']:,})"],
        [
            "세후소득",
            f"{corp_tax_results['income_after_tax']:,}",
        ],
    ]
    print("\n")
    print(tabulate(data, headers=["항목(법인사업자)", "금액(원)"], colalign=("left", "right")))

    print("\n")
    income_diff = (
        corp_tax_results["income_after_tax"] - sole_tax_results["income_after_tax"]
    )
    if income_diff >= 0:
        print(f"법인사업자(유리) > 개인사업자: {income_diff}원")
    else:
        print(f"법인사업자 < 개인사업자(유리): {income_diff*-1}원")


def main():
    gross_profit = int(input("매출총이익(단위:원)을 입력해주세요: "))
    sole_tax_results = get_sole_proprietorship_tax(gross_profit)
    corp_tax_results = get_corporation_tax(gross_profit)
    display_results(sole_tax_results, corp_tax_results)


if __name__ == "__main__":
    main()
