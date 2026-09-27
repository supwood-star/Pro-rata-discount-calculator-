import pandas as pd
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
st.caption("💡 提示：可直接在表格內修改，點擊表格底部的 `+` 可新增項目。")

# 預設資料
default_data = pd.DataFrame(
    [
        {"餐點名稱": "鐵板雞扒套餐", "原價 ($)": 94.0},
        {"餐點名稱": "脆皮燒雞 (半隻)", "原價 ($)": 130.0},
        {"餐點名稱": "套餐 B (燒雞+牛腩)", "原價 ($)": 131.0},
    ]
)

# 2. 用可編輯表格讓使用者直接操作 (支援新增/刪除/修改)
edited_df = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "餐點名稱": st.column_config.TextColumn(
            "餐點名稱", required=True, default="新餐點"
        ),
        "原價 ($)": st.column_config.NumberColumn(
            "原價 ($)", min_value=0.0, format="$%.2f", default=0.0
        ),
    },
)

st.divider()

# 3. 計算按鈕
if st.button("🧮 計算分攤金額", type="primary", use_container_width=True):
    # 過濾出有效的餐點
    valid_items = edited_df[edited_df["原價 ($)"] > 0].to_dict("records")
    total_original = sum(item["原價 ($)"] for item in valid_items)

    if total_original <= 0:
        st.error("請在表格中輸入至少一個大於 $0 的餐點原價！")
    elif total_paid <= 0:
        st.error("請輸入有效的實付總額！")
    else:
        # 按比例計算
        current_sum = 0.0
        results = []

        for item in valid_items:
            share = (item["原價 ($)"] / total_original) * total_paid
            rounded_share = round(share, 2)
            results.append(
                {
                    "name": item["餐點名稱"],
                    "price": item["原價 ($)"],
                    "share": rounded_share,
                }
            )
            current_sum += rounded_share

        # 自動修正 $0.01 尾數誤差
        diff = round(total_paid - current_sum, 2)
        if diff != 0 and len(results) > 0:
            max_item = max(results, key=lambda x: x["price"])
            max_item["share"] = round(max_item["share"] + diff, 2)

        # 顯示統計數據
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
