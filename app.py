import streamlit as st
import pandas as pd
import datetime
import os

# --- Настройки страницы ---
st.set_page_config(page_title="CFO Dashboard", page_icon="🍏", layout="centered")

# --- Базовая защита по паролю ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "Af809747": # ТВОЙ ПАРОЛЬ (измени его)
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Введи пароль для доступа", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Введи пароль для доступа", type="password", on_change=password_entered, key="password")
        st.error("Неверный пароль")
        return False
    return True

if check_password():
    # --- Apple Style CSS ---
    st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "San Francisco", Roboto, Helvetica, Arial, sans-serif;
            background-color: #F2F2F7;
            color: #1C1C1E;
        }
        .ios-card {
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.4);
        }
        h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; }
        .metric-value { font-size: 36px; font-weight: 700; margin: 0; color: #000; }
        .metric-label { font-size: 13px; color: #8E8E93; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; letter-spacing: 0.5px;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # --- База данных (CSV) ---
    DATA_FILE = "finance_db.csv"
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['Дата', 'Тип', 'Категория', 'Сумма', 'Комментарий'])
        df.to_csv(DATA_FILE, index=False)
    
    df = pd.read_csv(DATA_FILE)

    # --- Расчеты ---
    current_month = datetime.date.today().strftime('%Y-%m')
    df['Дата'] = pd.to_datetime(df['Дата'])
    df_month = df[df['Дата'].dt.strftime('%Y-%m') == current_month]

    total_income = df_month[df_month['Тип'] == 'Доход']['Сумма'].sum()
    total_expense = df_month[df_month['Тип'] == 'Расход']['Сумма'].sum()
    saved = total_income - total_expense

    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Finance 🍏</h1>", unsafe_allow_html=True)

    # --- Дашборд ---
    st.markdown(f"""
    <div class="ios-card">
        <div class="metric-label">Накоплено за месяц</div>
        <div class="metric-value" style="color: #34C759;">{saved:,.0f} ₽</div>
        <div style="margin-top: 15px; display: flex; justify-content: space-between;">
            <div>
                <div class="metric-label">Поступления</div>
                <div style="font-size: 18px; font-weight: 600;">{total_income:,.0f} ₽</div>
            </div>
            <div style="text-align: right;">
                <div class="metric-label">Потрачено</div>
                <div style="font-size: 18px; font-weight: 600; color: #FF3B30;">{total_expense:,.0f} ₽</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Ввод данных ---
    st.markdown("### Новая операция")
    with st.form("add_tx_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tx_type = st.selectbox("Тип", ["Расход", "Доход"])
            amount = st.number_input("Сумма (₽)", min_value=0.0, step=100.0, format="%.2f")
        with col2:
            if tx_type == "Расход":
                category = st.selectbox("Категория", ["LIFE (Еда/Проезд)", "WANT (Игры/Кафе)", "LEAK (Утечки)"])
            else:
                category = st.selectbox("Категория", ["Мама", "Прочее"])
            date_input = st.date_input("Дата", datetime.date.today())
            
        comment = st.text_input("Комментарий")
        submitted = st.form_submit_button("Сохранить операцию")
        
        if submitted and amount > 0:
            new_data = pd.DataFrame({
                'Дата': [date_input],
                'Тип': [tx_type],
                'Категория': [category],
                'Сумма': [amount],
                'Комментарий': [comment]
            })
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Данные записаны!")
            st.rerun()

    # --- История ---
    st.markdown("### Последние операции")
    if not df.empty:
        st.dataframe(df.sort_values(by='Дата', ascending=False).head(10), use_container_width=True, hide_index=True)
    else:
        st.info("История пуста.")
      
