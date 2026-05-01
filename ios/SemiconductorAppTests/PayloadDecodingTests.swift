import XCTest
@testable import SemiconductorApp

final class PayloadDecodingTests: XCTestCase {
    func testDecodesCorePayloadAndLimitUpRule() throws {
        let json = """
        {
          "data": [
            {
              "code": "000001",
              "name": "Test Co",
              "business_type": "设备",
              "region": "上海",
              "change_pct": 10.01,
              "invest_score": 82,
              "is_pick": true
            }
          ],
          "news_pool": [],
          "kline_data": {},
          "industry_intro": [],
          "industry_basics": [],
          "industry_source_refs": [],
          "industry_intro_source": "test",
          "global_compare_items": [],
          "global_compare_refs": [],
          "data_time": "2026-01-01 00:00:00",
          "data_time_iso": "2026-01-01T00:00:00+08:00"
        }
        """
        let payload = try JSONDecoder().decode(DashboardPayload.self, from: Data(json.utf8))
        XCTAssertEqual(payload.data.count, 1)
        XCTAssertTrue(payload.data[0].isLimitUp)
        XCTAssertEqual(payload.data[0].scoreTier, .high)
    }
}
