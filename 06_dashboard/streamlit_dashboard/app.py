from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="NutriMatch Data Science Dashboard",
    layout="wide",
)


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
DATASET_CANDIDATES = [
    os.environ.get("NUTRIMATCH_DATASET_PATH"),
    APP_DIR / "data" / "train_ready_dataset.csv",
    APP_DIR.parent.parent / "03_final_datasets" / "main" / "train_ready_dataset.csv",
    REPO_ROOT / "orang_b" / "final_datasets" / "train_ready_dataset.csv",
    REPO_ROOT / "data" / "ready" / "train_ready_dataset.csv",
    REPO_ROOT / "train_ready_dataset.csv",
]

PROFILE_SCHEMA_CANDIDATES = [
    os.environ.get("NUTRIMATCH_PROFILE_SCHEMA_PATH"),
    APP_DIR / "data" / "user_profile_features_schema.csv",
    APP_DIR.parent.parent / "03_final_datasets" / "main" / "user_profile_features_schema.csv",
    REPO_ROOT / "data" / "ready" / "user_profile_features_schema.csv",
    REPO_ROOT / "user_profile_features_schema.csv",
]


NUMERIC_COLUMNS = [
    "calories_100g",
    "protein_100g",
    "fat_100g",
    "carbohydrate_100g",
    "calorie_macro_diff",
    "allergen_match_count",
    "recommendation_confidence",
]

PROFILE_NUMERIC_COLUMNS = [
    "age",
    "height_cm",
    "weight_kg",
    "bmr",
    "tdee",
    "target_calorie",
    "protein_target_g",
    "fat_target_g",
    "carb_target_g",
    "total_macro_kcal",
    "macro_cal_diff",
]

BOOLEAN_COLUMNS = [
    "is_recommendable_food",
    "is_halal_candidate",
    "contains_non_halal_ingredient",
    "meal_combo_valid",
    "suitable_breakfast",
    "suitable_lunch",
    "suitable_dinner",
    "ingredient_only_flag",
    "raw_ingredient_flag",
]


def find_dataset_path() -> Path:
    for candidate in DATASET_CANDIDATES:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    searched = "\n".join(f"- {Path(p)}" for p in DATASET_CANDIDATES if p)
    raise FileNotFoundError(f"Dataset tidak ditemukan. Lokasi yang dicek:\n{searched}")


def find_optional_path(candidates: list[object]) -> Path | None:
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    return None


def split_tags(value: object) -> list[str]:
    if pd.isna(value):
        return []
    raw = str(value).strip().lower()
    if not raw or raw == "nan":
        return []
    tags = [part.strip() for part in re.split(r"[|,;/]", raw) if part.strip()]
    return list(dict.fromkeys(tags))


def bool_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes", "y", "ya"})
    )


def normalized(series: pd.Series, invert: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum == minimum:
        scores = pd.Series(0.5, index=series.index)
    else:
        scores = (values - minimum) / (maximum - minimum)
    return 1 - scores if invert else scores


@st.cache_data(show_spinner=False)
def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = bool_series(df[column])

    if "food_name_clean" in df.columns:
        df["_display_name"] = df["food_name_clean"].fillna(df.get("food_name", ""))
    else:
        df["_display_name"] = df.get("food_name", pd.Series(index=df.index, dtype=str))
    df["_display_name"] = df["_display_name"].fillna("").astype(str)

    if "meal_time_tags" in df.columns:
        df["_meal_tags"] = df["meal_time_tags"].apply(split_tags)
    elif "meal_time" in df.columns:
        df["_meal_tags"] = df["meal_time"].apply(split_tags)
    else:
        df["_meal_tags"] = [[] for _ in range(len(df))]

    df["_ingredient_tags"] = [[] for _ in range(len(df))]
    if "base_ingredient_tags" in df.columns:
        df["_ingredient_tags"] = df["base_ingredient_tags"].apply(split_tags)
    elif "main_ingredient" in df.columns:
        df["_ingredient_tags"] = df["main_ingredient"].apply(split_tags)

    protein_score = normalized(df.get("protein_100g", pd.Series(0, index=df.index)))
    calorie_score = normalized(df.get("calories_100g", pd.Series(0, index=df.index)), invert=True)
    fat_score = normalized(df.get("fat_100g", pd.Series(0, index=df.index)), invert=True)

    recommendable = (
        df["is_recommendable_food"].astype(float)
        if "is_recommendable_food" in df.columns
        else pd.Series(1.0, index=df.index)
    )
    combo_valid = (
        df["meal_combo_valid"].astype(float)
        if "meal_combo_valid" in df.columns
        else pd.Series(0.5, index=df.index)
    )
    halal_candidate = (
        df["is_halal_candidate"].astype(float)
        if "is_halal_candidate" in df.columns
        else pd.Series(0.5, index=df.index)
    )

    df["_qa_score"] = (
        protein_score * 0.35
        + calorie_score * 0.20
        + fat_score * 0.15
        + recommendable * 0.15
        + combo_valid * 0.10
        + halal_candidate * 0.05
    ) * 100
    return df


@st.cache_data(show_spinner=False)
def load_profile_schema(path: str | None) -> pd.DataFrame:
    if not path:
        return pd.DataFrame()
    df = pd.read_csv(path)
    for column in PROFILE_NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def count_values(df: pd.DataFrame, column: str, top: int = 12) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame(columns=[column, "count"])
    values = (
        df[column]
        .fillna("unknown")
        .astype(str)
        .replace({"": "unknown", "nan": "unknown"})
        .value_counts()
        .head(top)
        .reset_index()
    )
    values.columns = [column, "count"]
    return values


def all_tags(df: pd.DataFrame, column: str) -> list[str]:
    tags: set[str] = set()
    for values in df[column]:
        tags.update(values)
    return sorted(tags)


def filter_by_tag(df: pd.DataFrame, column: str, selected: list[str]) -> pd.DataFrame:
    if not selected:
        return df
    selected_set = set(selected)
    return df[df[column].apply(lambda values: bool(selected_set.intersection(values)))]


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filter")

    search = st.sidebar.text_input("Cari makanan", placeholder="contoh: ayam, nasi, tempe")
    filtered = df.copy()
    if search:
        haystack = filtered["_display_name"].str.lower()
        if "food_name" in filtered.columns:
            haystack = haystack + " " + filtered["food_name"].fillna("").astype(str).str.lower()
        filtered = filtered[haystack.str.contains(search.lower(), regex=False)]

    if "is_recommendable_food" in filtered.columns:
        recommendable_only = st.sidebar.checkbox("Tampilkan item rekomendasi saja", value=True)
        if recommendable_only:
            filtered = filtered[filtered["is_recommendable_food"]]

    meal_options = all_tags(df, "_meal_tags")
    selected_meals = st.sidebar.multiselect("Waktu makan", meal_options)
    filtered = filter_by_tag(filtered, "_meal_tags", selected_meals)

    component_col = "meal_component" if "meal_component" in filtered.columns else "food_category"
    if component_col in filtered.columns:
        component_options = sorted(filtered[component_col].dropna().astype(str).unique())
        selected_components = st.sidebar.multiselect("Komposisi makanan", component_options)
        if selected_components:
            filtered = filtered[filtered[component_col].astype(str).isin(selected_components)]

    if "dish_type" in filtered.columns:
        dish_options = sorted(filtered["dish_type"].dropna().astype(str).unique())
        selected_dish_types = st.sidebar.multiselect("Jenis masakan", dish_options)
        if selected_dish_types:
            filtered = filtered[filtered["dish_type"].astype(str).isin(selected_dish_types)]

    ingredient_options = all_tags(filtered, "_ingredient_tags")
    selected_ingredients = st.sidebar.multiselect("Bahan dasar", ingredient_options)
    filtered = filter_by_tag(filtered, "_ingredient_tags", selected_ingredients)

    if "halal_status" in filtered.columns:
        halal_options = sorted(filtered["halal_status"].dropna().astype(str).unique())
        selected_halal = st.sidebar.multiselect("Status halal", halal_options)
        if selected_halal:
            filtered = filtered[filtered["halal_status"].astype(str).isin(selected_halal)]

    if "image_url_status" in filtered.columns:
        image_options = sorted(filtered["image_url_status"].dropna().astype(str).unique())
        selected_images = st.sidebar.multiselect("Status gambar", image_options)
        if selected_images:
            filtered = filtered[filtered["image_url_status"].astype(str).isin(selected_images)]

    if "calories_100g" in filtered.columns and filtered["calories_100g"].notna().any():
        minimum = int(max(0, filtered["calories_100g"].min()))
        maximum = int(max(1, filtered["calories_100g"].max()))
        selected_range = st.sidebar.slider("Kalori per 100g", minimum, maximum, (minimum, maximum))
        filtered = filtered[
            filtered["calories_100g"].between(selected_range[0], selected_range[1], inclusive="both")
        ]

    return filtered


def metric_card(label: str, value: object, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)


def show_overview(df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    metric_cols = st.columns(5)
    with metric_cols[0]:
        metric_card("Total item", f"{len(filtered):,}", "Jumlah item setelah filter")
    with metric_cols[1]:
        if "is_recommendable_food" in filtered.columns:
            metric_card("Recommendable", f"{int(filtered['is_recommendable_food'].sum()):,}")
        else:
            metric_card("Recommendable", "-")
    with metric_cols[2]:
        if "is_halal_candidate" in filtered.columns:
            metric_card("Halal candidate", f"{int(filtered['is_halal_candidate'].sum()):,}")
        else:
            metric_card("Halal candidate", "-")
    with metric_cols[3]:
        if "calories_100g" in filtered.columns:
            metric_card("Rata-rata kalori", f"{filtered['calories_100g'].mean():.1f}")
        else:
            metric_card("Rata-rata kalori", "-")
    with metric_cols[4]:
        if "image_url_status" in filtered.columns:
            image_ok = filtered["image_url_status"].isin(["ok", "refreshed"]).sum()
            metric_card("Gambar siap", f"{int(image_ok):,}")
        else:
            metric_card("Gambar siap", "-")

    chart_cols = st.columns(3)
    with chart_cols[0]:
        component_col = "meal_component" if "meal_component" in filtered.columns else "food_category"
        component_counts = count_values(filtered, component_col)
        if not component_counts.empty:
            st.plotly_chart(
                px.bar(
                    component_counts,
                    x="count",
                    y=component_col,
                    orientation="h",
                    title="Distribusi komposisi makanan",
                    color="count",
                    color_continuous_scale="Tealgrn",
                ).update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False),
                use_container_width=True,
            )

    with chart_cols[1]:
        dish_counts = count_values(filtered, "dish_type") if "dish_type" in filtered.columns else pd.DataFrame()
        if not dish_counts.empty:
            st.plotly_chart(
                px.bar(
                    dish_counts,
                    x="count",
                    y="dish_type",
                    orientation="h",
                    title="Distribusi jenis masakan",
                    color="count",
                    color_continuous_scale="Mint",
                ).update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False),
                use_container_width=True,
            )

    with chart_cols[2]:
        meal_counts = (
            filtered[["_meal_tags"]]
            .explode("_meal_tags")
            .dropna()
            .rename(columns={"_meal_tags": "meal_time"})
        )
        if not meal_counts.empty:
            meal_counts = meal_counts["meal_time"].value_counts().reset_index()
            meal_counts.columns = ["meal_time", "count"]
            st.plotly_chart(
                px.pie(
                    meal_counts,
                    names="meal_time",
                    values="count",
                    title="Distribusi waktu makan",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                ),
                use_container_width=True,
            )

    scatter_cols = [
        column
        for column in ["calories_100g", "protein_100g", "fat_100g", "carbohydrate_100g"]
        if column in filtered.columns
    ]
    if {"calories_100g", "protein_100g"}.issubset(scatter_cols):
        color_col = "meal_component" if "meal_component" in filtered.columns else ("food_category" if "food_category" in filtered.columns else None)
        st.plotly_chart(
            px.scatter(
                filtered,
                x="calories_100g",
                y="protein_100g",
                color=color_col,
                hover_name="_display_name",
                size="fat_100g" if "fat_100g" in filtered.columns else None,
                title="Peta nutrisi: kalori vs protein",
            ),
            use_container_width=True,
        )

    if len(filtered) != len(df):
        st.caption(f"Filter aktif: {len(filtered):,} dari {len(df):,} item.")


def show_explorer(filtered: pd.DataFrame) -> None:
    st.subheader("Food Explorer")
    sort_col = st.selectbox(
        "Urutkan",
        [column for column in ["_qa_score", "protein_100g", "calories_100g", "food_name_clean"] if column in filtered.columns],
        index=0,
    )
    ascending = st.checkbox("Urutan naik", value=False)
    table = filtered.sort_values(sort_col, ascending=ascending).copy()

    columns = [
        column
        for column in [
            "food_id",
            "food_name",
            "meal_component",
            "dish_type",
            "base_ingredient",
            "meal_time_tags",
            "halal_status",
            "calories_100g",
            "protein_100g",
            "fat_100g",
            "carbohydrate_100g",
            "pairing_group",
            "meal_template_role",
            "image_url_status",
        ]
        if column in table.columns
    ]
    table_display = table[columns].head(250)
    st.dataframe(table_display, use_container_width=True, hide_index=True)

    csv = table[columns].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download hasil filter",
        data=csv,
        file_name="nutrimatch_filtered_train_ready.csv",
        mime="text/csv",
    )

    if "image_url" in table.columns:
        st.subheader("Preview gambar")
        preview_count = st.slider("Jumlah preview", 3, 24, 9)
        preview_rows = table.head(preview_count).to_dict("records")
        for start in range(0, len(preview_rows), 3):
            cols = st.columns(3)
            for col, row in zip(cols, preview_rows[start : start + 3]):
                with col:
                    st.image(row.get("image_url", ""), use_container_width=True)
                    st.caption(str(row.get("food_name", row.get("_display_name", ""))))


def show_nutrition_allergy(filtered: pd.DataFrame, profile_df: pd.DataFrame) -> None:
    st.subheader("Nutrisi Makanan")
    st.caption(
        "Bagian ini membaca nutrisi dari dataset makanan. BMR, TDEE, dan target makro berasal dari schema profil user di bagian bawah."
    )

    macro_cols = st.columns(4)
    with macro_cols[0]:
        if "calories_100g" in filtered.columns:
            metric_card("Rata-rata kalori", f"{filtered['calories_100g'].mean():.1f} kcal/100g")
    with macro_cols[1]:
        if "protein_100g" in filtered.columns:
            metric_card("Rata-rata protein", f"{filtered['protein_100g'].mean():.1f} g/100g")
    with macro_cols[2]:
        if "fat_100g" in filtered.columns:
            metric_card("Rata-rata lemak", f"{filtered['fat_100g'].mean():.1f} g/100g")
    with macro_cols[3]:
        if "carbohydrate_100g" in filtered.columns:
            metric_card("Rata-rata karbo", f"{filtered['carbohydrate_100g'].mean():.1f} g/100g")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        if "calories_100g" in filtered.columns:
            st.plotly_chart(
                px.histogram(
                    filtered,
                    x="calories_100g",
                    nbins=30,
                    title="Distribusi kalori per 100g",
                    color_discrete_sequence=["#0f766e"],
                ),
                use_container_width=True,
            )
    with chart_cols[1]:
        if {"protein_100g", "carbohydrate_100g", "fat_100g"}.issubset(filtered.columns):
            macro_mean = pd.DataFrame(
                {
                    "macro": ["Protein", "Karbohidrat", "Lemak"],
                    "g_per_100g": [
                        filtered["protein_100g"].mean(),
                        filtered["carbohydrate_100g"].mean(),
                        filtered["fat_100g"].mean(),
                    ],
                }
            )
            st.plotly_chart(
                px.bar(
                    macro_mean,
                    x="macro",
                    y="g_per_100g",
                    title="Rata-rata makro per 100g",
                    color="macro",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                ).update_layout(showlegend=False),
                use_container_width=True,
            )

    st.subheader("Alergen")
    allergen_columns = [
        column
        for column in [
            "contains_gluten",
            "contains_dairy",
            "contains_nuts",
            "contains_peanut",
            "contains_seafood",
            "contains_egg",
            "contains_soy",
            "contains_celery",
            "contains_mustard",
            "contains_sesame",
            "contains_sulfite",
            "contains_other",
            "contains_unknown",
        ]
        if column in filtered.columns
    ]

    if allergen_columns:
        allergen_counts = pd.DataFrame(
            {
                "allergen_flag": allergen_columns,
                "count": [int(bool_series(filtered[column]).sum()) for column in allergen_columns],
            }
        ).sort_values("count", ascending=False)
        st.plotly_chart(
            px.bar(
                allergen_counts,
                x="count",
                y="allergen_flag",
                orientation="h",
                title="Jumlah item berdasarkan flag alergen",
                color="count",
                color_continuous_scale="Oranges",
            ).update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False),
            use_container_width=True,
        )

        allergen_table_cols = [
            column
            for column in [
                "food_name",
                "confidence",
                "allergen_sources",
                "label_sources",
                "contains_gluten",
                "contains_dairy",
                "contains_peanut",
                "contains_seafood",
                "contains_egg",
                "contains_soy",
                "contains_unknown",
            ]
            if column in filtered.columns
        ]
        st.dataframe(filtered[allergen_table_cols].head(250), use_container_width=True, hide_index=True)
    else:
        st.info("Kolom flag alergen tidak ditemukan di dataset aktif.")

    st.subheader("Schema Profil User: BMR, TDEE, dan Target Makro")
    if profile_df.empty:
        st.info(
            "File `user_profile_features_schema.csv` belum ditemukan. BMR/TDEE bukan kolom makanan, jadi perlu file schema profil user untuk menampilkannya."
        )
        return

    profile_cols = st.columns(4)
    with profile_cols[0]:
        if "bmr" in profile_df.columns:
            metric_card("Rata-rata BMR", f"{profile_df['bmr'].mean():.1f}")
    with profile_cols[1]:
        if "tdee" in profile_df.columns:
            metric_card("Rata-rata TDEE", f"{profile_df['tdee'].mean():.1f}")
    with profile_cols[2]:
        if "target_calorie" in profile_df.columns:
            metric_card("Rata-rata target kalori", f"{profile_df['target_calorie'].mean():.1f}")
    with profile_cols[3]:
        metric_card("Sample profil", f"{len(profile_df):,}")

    profile_chart_cols = st.columns(2)
    with profile_chart_cols[0]:
        if "goal" in profile_df.columns:
            st.plotly_chart(
                px.bar(count_values(profile_df, "goal"), x="goal", y="count", title="Distribusi goal user"),
                use_container_width=True,
            )
    with profile_chart_cols[1]:
        if "activity_level" in profile_df.columns:
            st.plotly_chart(
                px.bar(
                    count_values(profile_df, "activity_level"),
                    x="activity_level",
                    y="count",
                    title="Distribusi activity level",
                ),
                use_container_width=True,
            )

    display_cols = [
        column
        for column in [
            "age",
            "gender",
            "height_cm",
            "weight_kg",
            "activity_level",
            "goal",
            "bmr",
            "tdee",
            "target_calorie",
            "protein_target_g",
            "fat_target_g",
            "carb_target_g",
            "allergy_vector",
        ]
        if column in profile_df.columns
    ]
    st.dataframe(profile_df[display_cols].head(250), use_container_width=True, hide_index=True)


def show_recommendation_qa(filtered: pd.DataFrame) -> None:
    st.subheader("Recommendation QA")
    st.caption(
        "Skor QA ini bukan model final. Skor dipakai untuk audit cepat supaya kandidat rekomendasi tidak hanya didominasi makanan bernutrisi tinggi yang sama."
    )

    top_n = st.slider("Top item per grup", 3, 20, 8)
    group_col = st.selectbox(
        "Kelompok audit",
        [
            column
            for column in ["primary_meal_time", "meal_component", "dish_type", "pairing_group", "base_ingredient"]
            if column in filtered.columns
        ],
    )
    ranked = filtered.sort_values("_qa_score", ascending=False).copy()
    ranked["_rank_in_group"] = ranked.groupby(group_col)["_qa_score"].rank(method="first", ascending=False)
    ranked = ranked[ranked["_rank_in_group"] <= top_n]

    cols = [
        column
        for column in [
            "food_name",
            group_col,
            "_qa_score",
            "calories_100g",
            "protein_100g",
            "fat_100g",
            "meal_time_tags",
            "halal_status",
            "pairing_role",
            "pairing_notes",
        ]
        if column in ranked.columns
    ]
    st.dataframe(ranked[cols].sort_values([group_col, "_qa_score"], ascending=[True, False]), use_container_width=True, hide_index=True)

    if "pairing_group" in filtered.columns:
        pairing_counts = count_values(filtered, "pairing_group", top=15)
        st.plotly_chart(
            px.bar(
                pairing_counts,
                x="pairing_group",
                y="count",
                title="Sebaran pairing group untuk variasi rekomendasi",
                color="count",
                color_continuous_scale="Mint",
            ),
            use_container_width=True,
        )


def show_dataset_audit(filtered: pd.DataFrame) -> None:
    st.subheader("Dataset Audit")
    audit_cols = st.columns(3)
    with audit_cols[0]:
        if "cleaning_action" in filtered.columns:
            st.plotly_chart(
                px.bar(count_values(filtered, "cleaning_action"), x="cleaning_action", y="count", title="Cleaning action"),
                use_container_width=True,
            )
    with audit_cols[1]:
        if "halal_status" in filtered.columns:
            st.plotly_chart(
                px.bar(count_values(filtered, "halal_status"), x="halal_status", y="count", title="Halal status"),
                use_container_width=True,
            )
    with audit_cols[2]:
        if "image_url_status" in filtered.columns:
            st.plotly_chart(
                px.bar(count_values(filtered, "image_url_status"), x="image_url_status", y="count", title="Image URL status"),
                use_container_width=True,
            )

    audit_columns = [
        column
        for column in [
            "food_id",
            "food_name",
            "cleaning_action",
            "cleaning_reason",
            "recommendation_exclusion_reason",
            "halal_review_reason",
            "image_url_status",
            "image_url_source",
            "source",
        ]
        if column in filtered.columns
    ]
    st.dataframe(filtered[audit_columns], use_container_width=True, hide_index=True)


def main() -> None:
    dataset_path = find_dataset_path()
    profile_schema_path = find_optional_path(PROFILE_SCHEMA_CANDIDATES)
    df = load_dataset(str(dataset_path))
    profile_df = load_profile_schema(str(profile_schema_path) if profile_schema_path else None)

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        [data-testid="stMetricValue"] { font-size: 1.7rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("NutriMatch Data Science Dashboard")
    profile_caption = (
        f" | Schema profil: {profile_schema_path.name}"
        if profile_schema_path
        else " | Schema profil: tidak ditemukan"
    )
    st.caption(f"Dataset aktif: {dataset_path.name} | {len(df):,} item train-ready{profile_caption}")

    filtered = apply_filters(df)
    if filtered.empty:
        st.warning("Tidak ada data yang cocok dengan filter saat ini.")
        st.stop()

    tabs = st.tabs(["Overview", "Nutrisi & Alergi", "Food Explorer", "Recommendation QA", "Dataset Audit"])
    with tabs[0]:
        show_overview(df, filtered)
    with tabs[1]:
        show_nutrition_allergy(filtered, profile_df)
    with tabs[2]:
        show_explorer(filtered)
    with tabs[3]:
        show_recommendation_qa(filtered)
    with tabs[4]:
        show_dataset_audit(filtered)


if __name__ == "__main__":
    main()
