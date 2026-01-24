/**
 * 사주 계산 패키지 - 타입 정의
 *
 * @author SajuApp
 * @version 1.0.0
 */
// ============================================================
// 타입 가드
// ============================================================
export function isCompleteSajuData(data) {
    return data &&
        data.isComplete === true &&
        data.version !== undefined &&
        data.fourPillars !== undefined &&
        data.daewoon !== undefined;
}
export function hasMinimalSajuData(data) {
    return data &&
        data.year?.gan !== undefined &&
        data.month?.gan !== undefined &&
        data.day?.gan !== undefined &&
        data.time?.gan !== undefined;
}
//# sourceMappingURL=types.js.map