import SwiftUI

struct StockDetailView: View {
    let stock: StockItem

    var body: some View {
        List {
            Section(stock.name) {
                metricRow("Code", stock.code)
                metricRow("Board", stock.board ?? "N/A")
                metricRow("Business", stock.businessType ?? "N/A")
                metricRow("Region", stock.region ?? "N/A")
            }
            Section("Market") {
                metricRow("Price", AppFormatters.number(stock.price))
                metricRow("Change", AppFormatters.percent(stock.changePct))
                metricRow("Market Cap (100M CNY)", AppFormatters.number(stock.marketCap))
                metricRow("Forward P/E", AppFormatters.number(stock.peForward))
                metricRow("Trailing P/E", AppFormatters.number(stock.peTrailing))
                metricRow("Volume", AppFormatters.number(stock.volume, digits: 0))
            }
            Section("Decision") {
                metricRow("Score", "\(stock.investScore ?? 0)")
                metricRow("Grade", stock.investGrade ?? "-")
                metricRow("Tags", stock.investTags ?? "-")
                Text(stock.investReason ?? "N/A")
                    .font(.callout)
            }
        }
        .navigationTitle(stock.name)
    }

    private func metricRow(_ key: String, _ value: String) -> some View {
        HStack {
            Text(key).foregroundStyle(.secondary)
            Spacer()
            Text(value)
        }
    }
}
