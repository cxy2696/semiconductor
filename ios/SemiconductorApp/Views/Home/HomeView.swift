import Charts
import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    private var topSegments: [(String, Int)] {
        let grouped = Dictionary(grouping: viewModel.filteredStocks, by: { $0.chainSegment ?? "Other" })
        return grouped.map { ($0.key, $0.value.count) }
            .sorted(by: { $0.1 > $1.1 })
            .prefix(6)
            .map { $0 }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                let iso = viewModel.payload.dataTimeISO
                if !iso.isEmpty {
                    Text(AppFormatters.localizedDate(
                        iso,
                        localeId: viewModel.localeProfile.localeIdentifier,
                        timeZoneId: viewModel.localeProfile.timeZoneIdentifier
                    ))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }

                SummaryCardsView(stocks: viewModel.filteredStocks)

                GroupBox(viewModel.text(.decisionSupport)) {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(viewModel.decisionCandidates.prefix(4)) { stock in
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(stock.name).font(.headline)
                                    Text("\(stock.code) · \(stock.businessType ?? "N/A")")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer()
                                Text("\(stock.investScore ?? 0)")
                                    .font(.title3.bold())
                            }
                        }
                    }
                }

                GroupBox(viewModel.text(.limitUpBoard)) {
                    VStack(alignment: .leading, spacing: 8) {
                        if viewModel.limitUpStocks.isEmpty {
                            Text(viewModel.text(.noLimitUp))
                                .font(.callout)
                                .foregroundStyle(.secondary)
                        } else {
                            ForEach(viewModel.limitUpStocks.prefix(10)) { stock in
                                HStack {
                                    Text(stock.name).font(.subheadline.bold())
                                    Spacer()
                                    Text(AppFormatters.percent(stock.changePct))
                                        .foregroundStyle(.red)
                                }
                            }
                        }
                    }
                }

                GroupBox(viewModel.text(.segmentDistribution)) {
                    Chart(topSegments, id: \.0) { item in
                        BarMark(
                            x: .value("Segment", item.0),
                            y: .value("Count", item.1)
                        )
                    }
                    .frame(height: 220)
                }
            }
            .padding()
        }
        .navigationTitle(viewModel.text(.homeTitle))
        .refreshable {
            await viewModel.loadData(force: true)
        }
    }
}

private struct SummaryCardsView: View {
    let stocks: [StockItem]

    var body: some View {
        let avg = stocks.compactMap(\.changePct)
        let avgPct = avg.isEmpty ? nil : avg.reduce(0, +) / Double(avg.count)
        let top = stocks.max(by: { ($0.changePct ?? -999) < ($1.changePct ?? -999) })
        let low = stocks.min(by: { ($0.changePct ?? 999) < ($1.changePct ?? 999) })

        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            Card(title: "Companies", value: "\(stocks.count)", subtitle: "In current filters")
            Card(title: "Average Change", value: AppFormatters.percent(avgPct), subtitle: "Daily")
            Card(title: "Top Gainer", value: top?.name ?? "N/A", subtitle: AppFormatters.percent(top?.changePct))
            Card(title: "Top Loser", value: low?.name ?? "N/A", subtitle: AppFormatters.percent(low?.changePct))
        }
    }
}

private struct Card: View {
    let title: String
    let value: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.caption).foregroundStyle(.secondary)
            Text(value).font(.headline)
            Text(subtitle).font(.caption2).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}
