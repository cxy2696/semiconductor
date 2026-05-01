import XCTest

final class SemiconductorAppUITests: XCTestCase {
    func testTabBarExists() throws {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.tabBars.firstMatch.waitForExistence(timeout: 5))
    }
}
