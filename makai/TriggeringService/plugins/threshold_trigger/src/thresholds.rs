/// Collection
/// makai_config {
///     triggering {
///         default_ref_f: float,
///         default_ref_v: float,
///         default_threshold_percent_v_low: float,
///         default_threshold_percent_v_high: float,
///         default_threshold_percent_f_low: float,
///         default_threshold_percent_f_high: float,
///         default_threshold_percent_thd_high: float,
///         overrides: []
///     }
/// }
///
/// where override is object of
/// {
///     box_id: str,
///     ref_f: float,
///     ref_v: float,
///     threshold_percent_v_low: float,
///     threshold_percent_v_high: float,
///     threshold_percent_f_low: float,
///     threshold_percent_f_high: float,
///     threshold_percent_thd_high: float,
/// }

struct CachedThresholdProvider {}
