"""
Stage 5 Seed Data: Diagnostic Assessment & 24 Deterministic Psychometric Questions.
Notice: Prototype assessment questions covering 8 core SIH26101 competencies.
"""

from typing import Any

DIAGNOSTIC_ASSESSMENT_TITLE = "PRAGYA Core Competency Diagnostic"
DIAGNOSTIC_ASSESSMENT_DESC = (
    "Comprehensive diagnostic evaluation benchmarking foundational and working competencies across "
    "core official statistical methodologies, data engineering, spatial analysis, and modern analytics."
)

DIAGNOSTIC_COMPETENCY_CODES = [
    "STAT_SAMPLING",
    "STAT_SURVEY_DESIGN",
    "STAT_DATA_QUALITY_FRAMEWORKS",
    "TECH_PYTHON",
    "TECH_SQL",
    "TECH_DATA_VISUALIZATION",
    "TECH_GIS",
    "TECH_AI_ML",
]

DIAGNOSTIC_QUESTIONS: list[dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. STAT_SAMPLING
    # -------------------------------------------------------------------------
    {
        "competency_code": "STAT_SAMPLING",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "In Simple Random Sampling Without Replacement (SRSWOR), what is the probability that any "
            "specific unit from a population of size N is included in a sample of size n?"
        ),
        "options": [
            "n / N",
            "1 / N",
            "n / (N - 1)",
            "(n - 1) / N",
        ],
        "correct_option": 0,
        "explanation": "In SRSWOR, each unit in the finite population of size N has an equal first-order inclusion probability of pi_i = n / N.",
    },
    {
        "competency_code": "STAT_SAMPLING",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "Under Neyman Optimal Allocation in Stratified Random Sampling, how should the sample size n_h "
            "in stratum h be allocated when sampling costs per unit across strata are equal?"
        ),
        "options": [
            "Proportional to N_h * S_h (stratum size multiplied by stratum standard deviation)",
            "Proportional to N_h / S_h",
            "Equally divided across all strata regardless of size or variance",
            "Proportional to S_h^2 / N_h",
        ],
        "correct_option": 0,
        "explanation": "When unit sampling costs are uniform across strata, Neyman optimal allocation minimizes variance by distributing sample sizes proportional to N_h * S_h.",
    },
    {
        "competency_code": "STAT_SAMPLING",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "In two-stage cluster sampling, what does a Design Effect (Deff) of 2.4 indicate compared to "
            "a simple random sample of the same total size?"
        ),
        "options": [
            "The cluster design has 2.4 times larger variance than an SRS of equivalent sample size due to intra-cluster correlation",
            "The effective sample size is increased by 140%",
            "The cluster sample has 2.4 times smaller standard error than an SRS",
            "The survey implementation costs are reduced by a factor of 2.4",
        ],
        "correct_option": 0,
        "explanation": "The design effect Deff = Var(cluster) / Var(srs) = 1 + (m - 1)*rho. A Deff of 2.4 indicates that cluster homogeneity increases variance by 140% compared to SRS.",
    },

    # -------------------------------------------------------------------------
    # 2. STAT_SURVEY_DESIGN
    # -------------------------------------------------------------------------
    {
        "competency_code": "STAT_SURVEY_DESIGN",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "Which type of survey error cannot be reduced simply by increasing the total sample size?"
        ),
        "options": [
            "Non-sampling error (e.g. measurement bias, questionnaire ambiguity, non-response)",
            "Sampling variance",
            "Standard error of the estimated mean",
            "Margin of error under simple random sampling",
        ],
        "correct_option": 0,
        "explanation": "Non-sampling errors (such as questionnaire wording bias, respondent recall error, or systematic non-response) persist regardless of sample size.",
    },
    {
        "competency_code": "STAT_SURVEY_DESIGN",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "What is the primary objective of conducting a cognitive pilot test before finalizing a statistical survey questionnaire?"
        ),
        "options": [
            "To evaluate how respondents comprehend terminology, recall information, and formulate answers",
            "To finalize the statistical sampling weights",
            "To estimate the final national GDP aggregates",
            "To benchmark cloud database querying latency",
        ],
        "correct_option": 0,
        "explanation": "Cognitive pre-testing examines respondent comprehension, retrieval of information, judgment, and response selection to eliminate construct ambiguity.",
    },
    {
        "competency_code": "STAT_SURVEY_DESIGN",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "When compensating for unit non-response in household surveys, which technique adjusts sample weights "
            "based on known auxiliary population totals from census benchmarks?"
        ),
        "options": [
            "Calibration / Post-stratification weighting",
            "Hot-deck imputation for individual missing fields",
            "Winsorization of extreme observations",
            "Simple mean substitution",
        ],
        "correct_option": 0,
        "explanation": "Calibration weighting re-weights respondent samples so that weighted margins match known auxiliary population benchmarks, correcting for non-response bias.",
    },

    # -------------------------------------------------------------------------
    # 3. STAT_DATA_QUALITY_FRAMEWORKS
    # -------------------------------------------------------------------------
    {
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "Under the UN National Quality Assurance Framework (NQAF), which dimension measures the time lag "
            "between the reference period of the data and its public dissemination?"
        ),
        "options": [
            "Timeliness and Punctuality",
            "Relevance",
            "Coherence",
            "Accessibility and Clarity",
        ],
        "correct_option": 0,
        "explanation": "Timeliness refers to the lapse of time between the end of the reference period and the public dissemination of the statistical results.",
    },
    {
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "In official economic statistics, what does an audit of cross-period 'coherence and comparability' primarily verify?"
        ),
        "options": [
            "Consistency of statistical concepts, classifications, and methodologies across different sources and over time",
            "The physical encryption standards of database storage volumes",
            "The network bandwidth utilization during tablet survey uploads",
            "The total number of visitors to the statistical dissemination portal",
        ],
        "correct_option": 0,
        "explanation": "Coherence assesses whether statistics from different sources can be reliably combined, while comparability verifies stability of definitions over time.",
    },
    {
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "When validating micro-data from enterprise surveys, which deterministic check identifies logical violations "
            "between interconnected accounting variables?"
        ),
        "options": [
            "Relational edit rules (e.g. Total Output must equal Sold Products plus Additions to Stock)",
            "Univariate Z-score outlier filtering on isolated variables",
            "Random permutation testing",
            "K-means clustering on categorical industry codes",
        ],
        "correct_option": 0,
        "explanation": "Relational edit rules enforce structural accounting identities and mathematical constraints between interconnected survey fields, catching logical discrepancies.",
    },

    # -------------------------------------------------------------------------
    # 4. TECH_PYTHON
    # -------------------------------------------------------------------------
    {
        "competency_code": "TECH_PYTHON",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "In Python data manipulation with pandas, which approach is most computationally efficient for "
            "applying a mathematical transformation across millions of rows?"
        ),
        "options": [
            "Vectorized series operations (e.g., df['val'] * 1.05)",
            "Iterating with a standard Python for loop using range(len(df))",
            "Using df.iterrows() with row-by-row updates",
            "Exporting to CSV and re-importing with modified column types",
        ],
        "correct_option": 0,
        "explanation": "Vectorized operations in pandas/numpy execute compiled C-level loops, running orders of magnitude faster than Python-level iterations like iterrows().",
    },
    {
        "competency_code": "TECH_PYTHON",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "When processing a 40 GB statistical census file that exceeds available system RAM, which pandas "
            "technique enables efficient batch processing?"
        ),
        "options": [
            "Passing chunksize to pd.read_csv() inside an iteration loop",
            "Setting low_memory=False in pd.read_csv()",
            "Increasing the operating system swap file without modifying code",
            "Using df.to_pickle() before loading the file",
        ],
        "correct_option": 0,
        "explanation": "Specifying chunksize in pd.read_csv() returns a TextFileReader generator, enabling batch processing of large datasets without exhausting RAM.",
    },
    {
        "competency_code": "TECH_PYTHON",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "To prevent silent data corruption in pandas when merging two statistical survey datasets on a composite key, "
            "which parameter validates relationship cardinality?"
        ),
        "options": [
            "validate='one_to_one' or validate='one_to_many'",
            "indicator=True",
            "how='inner'",
            "suffixes=('_x', '_y')",
        ],
        "correct_option": 0,
        "explanation": "The validate argument checks whether merge keys are unique in either or both datasets, raising a MergeError if unexpected duplicates exist.",
    },

    # -------------------------------------------------------------------------
    # 5. TECH_SQL
    # -------------------------------------------------------------------------
    {
        "competency_code": "TECH_SQL",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "Which SQL clause is used to filter aggregated group results produced by a GROUP BY statement?"
        ),
        "options": [
            "HAVING",
            "WHERE",
            "ORDER BY",
            "DISTINCT",
        ],
        "correct_option": 0,
        "explanation": "The HAVING clause filters aggregated rows after grouping, whereas WHERE filters individual rows before grouping.",
    },
    {
        "competency_code": "TECH_SQL",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "Which SQL window function assigns ranks to survey respondents ordered by monthly expenditure without "
            "skipping rank numbers in case of identical ties?"
        ),
        "options": [
            "DENSE_RANK()",
            "RANK()",
            "ROW_NUMBER()",
            "NTILE(4)",
        ],
        "correct_option": 0,
        "explanation": "DENSE_RANK() computes sequential ranks where tied rows receive the same rank with no gaps in rank values (e.g. 1, 2, 2, 3), unlike RANK().",
    },
    {
        "competency_code": "TECH_SQL",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "In PostgreSQL, when querying large statistical survey tables with frequent multi-column filtering, "
            "which index strategy optimizes queries involving multiple column predicates with bitmap scans?"
        ),
        "options": [
            "Composite B-Tree index or combining single B-Trees via Bitmap Index Scans",
            "Hash index on a single text column",
            "Spatial GiST index on scalar integers",
            "BRIN index on high-cardinality random UUIDs",
        ],
        "correct_option": 0,
        "explanation": "Composite B-Tree indexes or combining single B-Trees via PostgreSQL Bitmap Index Scans allow efficient filtering across multiple correlated predicates.",
    },

    # -------------------------------------------------------------------------
    # 6. TECH_DATA_VISUALIZATION
    # -------------------------------------------------------------------------
    {
        "competency_code": "TECH_DATA_VISUALIZATION",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "Why should choropleth maps displaying state-level population statistics use rate or density metrics "
            "(e.g., persons per sq km) rather than raw absolute counts?"
        ),
        "options": [
            "To avoid visual distortion caused by large geographic land areas dominating visual weight regardless of population",
            "Because GIS software cannot render integer counts in thematic color palettes",
            "To conform to cartographic projection rules",
            "Because vector shapefiles only store floating point attributes",
        ],
        "correct_option": 0,
        "explanation": "Choropleth maps must display normalized densities or rates; otherwise, physically large but sparsely populated regions visually mislead users.",
    },
    {
        "competency_code": "TECH_DATA_VISUALIZATION",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "When designing statistical indicator dashboards for accessibility compliance (WCAG 2.1), "
            "what is an essential color palette consideration?"
        ),
        "options": [
            "Using colorblind-safe palettes (e.g., Viridis or ColorBrewer) and supporting colors with text labels or patterns",
            "Using only pure red and green indicators for status changes",
            "Limiting all charts to pure grayscale without any accent color",
            "Using high-saturation neon gradients across all charts",
        ],
        "correct_option": 0,
        "explanation": "Colorblind-safe palettes combined with dual-encoding (text or symbols alongside color) ensure data is interpretable by users with color vision deficiencies.",
    },
    {
        "competency_code": "TECH_DATA_VISUALIZATION",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "In Edward Tufte's principles of statistical data visualization, what does the 'Data-Ink Ratio' represent?"
        ),
        "options": [
            "The proportion of visual ink dedicated to the non-redundant display of data information versus decorative elements",
            "The physical volume of printer toner consumed by statistical tables",
            "The ratio of numerical digits to alphabetic characters in chart labels",
            "The resolution of SVG graphics compared to PNG raster files",
        ],
        "correct_option": 0,
        "explanation": "The Data-Ink Ratio is the share of graphic ink that cannot be erased without losing data information. Higher ratios signify clean, un-cluttered visual design.",
    },

    # -------------------------------------------------------------------------
    # 7. TECH_GIS
    # -------------------------------------------------------------------------
    {
        "competency_code": "TECH_GIS",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "What is the primary purpose of a Coordinate Reference System (CRS) such as EPSG:4326 (WGS 84) "
            "in geospatial statistical analysis?"
        ),
        "options": [
            "To define how two-dimensional coordinates relate to real physical locations on the Earth's surface",
            "To compress raster satellite imagery for web delivery",
            "To encrypt confidential survey GPS coordinates",
            "To convert tabular CSV files into relational database tables",
        ],
        "correct_option": 0,
        "explanation": "A CRS establishes the mathematical model (ellipsoid, datum, projection) translating coordinates on a map into physical Earth locations.",
    },
    {
        "competency_code": "TECH_GIS",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "When linking household survey GPS coordinates to district administrative boundary polygons, "
            "which GIS operation is performed?"
        ),
        "options": [
            "Spatial Join (Points in Polygon)",
            "Raster Map Algebra",
            "Network Shortest Path Routing",
            "Delaunay Triangulation",
        ],
        "correct_option": 0,
        "explanation": "A Spatial Join overlays point features onto polygon boundaries to inherit administrative attributes (district, state, block) based on topological containment.",
    },
    {
        "competency_code": "TECH_GIS",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "Why is an Equal-Area projection (such as Albers Equal Area Conic) preferred over Mercator when "
            "analyzing thematic statistical distributions across India?"
        ),
        "options": [
            "It preserves true relative surface area, ensuring density calculations and comparisons are mathematically accurate",
            "It preserves true compass bearing for marine navigation",
            "It enables faster GPU rendering in web browsers",
            "It eliminates the need for vector geometry validation",
        ],
        "correct_option": 0,
        "explanation": "Equal-area projections maintain accurate area ratios between geographic regions, preventing the severe latitudinal area distortion characteristic of Mercator.",
    },

    # -------------------------------------------------------------------------
    # 8. TECH_AI_ML
    # -------------------------------------------------------------------------
    {
        "competency_code": "TECH_AI_ML",
        "difficulty": "EASY",
        "points": 1,
        "question_text": (
            "In predictive machine learning for socio-economic indicators, what does 'overfitting' mean?"
        ),
        "options": [
            "The model memorizes noise and idiosyncrasies of the training data, failing to generalize to unseen test data",
            "The model has too few parameters to capture underlying patterns",
            "The training dataset contains too many observations",
            "The algorithm takes too long to converge during gradient descent",
        ],
        "correct_option": 0,
        "explanation": "Overfitting occurs when high model complexity captures spurious noise in training samples, causing poor predictive performance on validation/test sets.",
    },
    {
        "competency_code": "TECH_AI_ML",
        "difficulty": "MEDIUM",
        "points": 2,
        "question_text": (
            "When training time-series forecasting models on quarterly macroeconomic data, which validation "
            "strategy prevents temporal look-ahead leakage?"
        ),
        "options": [
            "Time-series split / Rolling-origin forward chaining (training only on past periods to predict future periods)",
            "Standard random K-fold cross-validation shuffling all years",
            "Stratified K-fold based on annual inflation rates",
            "Bootstrap resampling with replacement across all quarters",
        ],
        "correct_option": 0,
        "explanation": "Temporal cross-validation respects the chronological sequence of time-series data, ensuring the model is trained strictly on historical observations without look-ahead leakage.",
    },
    {
        "competency_code": "TECH_AI_ML",
        "difficulty": "HARD",
        "points": 3,
        "question_text": (
            "In an imbalanced survey classification problem where an event of interest occurs in only 2% of samples, "
            "why is ROC-AUC or Precision-Recall AUC preferred over standard accuracy?"
        ),
        "options": [
            "Accuracy can appear deceptively high (98%) for a naive classifier that predicts the majority class every time, whereas AUC measures discrimination across all decision thresholds",
            "Accuracy cannot be calculated on floating-point numbers",
            "AUC scales the target variable between -1 and +1",
            "Precision-Recall curves are only applicable to linear regression models",
        ],
        "correct_option": 0,
        "explanation": "On highly imbalanced datasets, a trivial model predicting the negative class attains 98% accuracy. AUC evaluates true positive and false positive trade-offs independently of class prevalence.",
    },
]
