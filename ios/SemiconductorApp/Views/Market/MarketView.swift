import SwiftUI

struct MarketView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        List {
            Section {
                Toggle(viewModel.text(.onlyPicks), isOn: $viewModel.onlyPicks)
                Menu("\(viewModel.text(.regions)) (\(viewModel.selectedRegions.count))") {
                    ForEach(viewModel.regions, id: \.self) { region in
                        Button {
                            if viewModel.selectedRegions.contains(region) {
                                viewModel.selectedRegions.remove(region)
                            } else {
                                viewModel.selectedRegions.insert(region)
                            }
                        } label: {
                            Label(region, systemImage: viewModel.selectedRegions.contains(region) ? "checkmark.circle.fill" : "circle")
                        }
                    }
                }
                Menu("\(viewModel.text(.business)) (\(viewModel.selectedBusinessTypes.count))") {
                    ForEach(viewModel.businessTypes, id: \.self) { biz in
                        Button {
                            if viewModel.selectedBusinessTypes.contains(biz) {
                                viewModel.selectedBusinessTypes.remove(biz)
                            } else {
                                viewModel.selectedBusinessTypes.insert(biz)
                            }
                        } label: {
                            Label(biz, systemImage: viewModel.selectedBusinessTypes.contains(biz) ? "checkmark.circle.fill" : "circle")
                        }
                    }
                }
            }

            Section(viewModel.text(.stocks)) {
                ForEach(viewModel.filteredStocks) { stock in
                    NavigationLink {
                        StockDetailView(stock: stock)
                    } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(stock.name).font(.headline)
                                Spacer()
                                Text(AppFormatters.percent(stock.changePct))
                                    .foregroundStyle((stock.changePct ?? 0) >= 0 ? .green : .red)
                            }
                            Text("\(stock.code) · \(stock.businessType ?? "N/A") · \(stock.region ?? "N/A")")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
        .searchable(text: $viewModel.query, prompt: viewModel.text(.searchPrompt))
        .navigationTitle(viewModel.text(.marketTitle))
        .refreshable {
            await viewModel.loadData(force: true)
        }
    }
}
