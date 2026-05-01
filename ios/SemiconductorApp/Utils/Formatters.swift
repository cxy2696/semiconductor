import Foundation

enum AppFormatters {
    static func number(_ value: Double?, digits: Int = 2) -> String {
        guard let value else { return "N/A" }
        return String(format: "%.\(digits)f", value)
    }

    static func percent(_ value: Double?) -> String {
        guard let value else { return "N/A" }
        return String(format: "%.2f%%", value)
    }

    static func localizedDate(_ value: String, localeId: String, timeZoneId: String) -> String {
        let parser = ISO8601DateFormatter()
        guard let date = parser.date(from: value) else { return value }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: localeId)
        formatter.timeZone = TimeZone(identifier: timeZoneId)
        formatter.dateStyle = .medium
        formatter.timeStyle = .medium
        return formatter.string(from: date)
    }
}
