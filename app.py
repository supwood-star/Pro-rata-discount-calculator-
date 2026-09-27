import streamlit as st

st.set_page_config(
    page_title="餐費 Pro-rata 拆數計算機", page_icon="🍔", layout="centered"
)

st.title("🍔 餐費 Pro-rata 拆數計算機")
st.caption("輸入實付總額與各餐點原價，自動按比例精確分攤（自動處理 $0.01 尾數）")

st.divider()

# 1. 輸入實付總額
total_paid = st.number_input(
    "請輸入最終實際支付總額 ($)",
    min_value=0.0,
    value=332.63,
    step=0.1,
    format="%.2f",
)

st.subheader("餐點 / 項目與原價")

# 初始化 session state 來記錄動態新增的項目
if "items" not in st.session_state:
    st.session_state.items = [
        {"name": "鐵板雞扒套餐", "price": 94.0},
        {"name": "脆皮燒雞 (半隻)", "price": 130.0},
        {"name": "套餐 B (燒雞+牛腩)", "price": 131.0},
    ]

# 動態新增項目按鈕
col_add, col_clear = st.columns([1, 1])
with col_add:
    if st.button("➕ 新增餐點"):
        st.session_state.items.append(
            {"name": f"餐點 {len(st.session_state.items) + 1}", "price": 0.0}
        )
        st.rerun()

with col_clear:
    if st.button("🗑️ 清空所有項目"):
        st.session_state.items = [{"name": "餐點 1", "price": 0.0}]
        st.rerun()

# 顯示輸入框
items_data = []
for i, item in enumerate(st.session_state.items):
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        name = st.text_input(
            f"餐點 {i+1} 名稱", value=item["name"], key=f"name_{i}"
        )
    with c2:
        price = st.number_input(
            f"原價 (${i+1})",
            min_value=0.0,
            value=float(item["price"]),
            step=1.0,
            format="%.2f",
            key=f"price_{i}",
        )
    with c3:
        st.write("")
        st.write("")
        if st.button("❌", key=f"del_{i}"):
            if len(st.session_state.items) > 1:
                st.session_state.items.pop(i)
                st.rerun()

    items_data.append({"name": name, "price": price})

st.divider()

# 計算按鈕
if st.button("🧮 計算分攤金額", type="primary", use_container_width=True):
    total_original = sum(x["price"] for x in items_data)

    if total_original <= 0:
        st.error("請輸入至少一個大於 $0 的餐點原價！")
    elif total_paid <= 0:
        st.error("請輸入有效的實付總額！")
    else:
        # 計算 pro-rata
        current_sum = 0.0
        results = []

        for item in items_data:
            share = (item["price"] / total_original) * total_paid
            rounded_share = round(share, 2)
            results.append(
                {
                    "name": item["name"],
                    "price": item["price"],
                    "share": rounded_share,
                }
            )
            current_sum += rounded_share

        # 修正 $0.01 尾數誤差
        diff = round(total_paid - current_sum, 2)
        if diff != 0:
            max_item = max(results, key=lambda x: x["price"])
            max_item["share"] = round(max_item["share"] + diff, 2)

        # 顯示統計數據
        discount_rate = (total_paid / total_original) * 100
        discount_fold = (total_paid / total_original) * 10

        st.success("計算成功！")
        st.metric(
            label="原價總額",
            value=f"${total_original:.2f}",
            delta=f"-${total_original - total_paid:.2f} (約 {discount_fold:.1f} 折)",
        )

        st.subheader("📊 分攤結果")
        for res in results:
            st.write(
                f"• **{res['name']}** (原價 ${res['price']:.2f}) $\\rightarrow$ 實付 **${res['share']:.2f}**"
            )
          
