import SwiftUI

struct CompareView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        List {
            Section(viewModel.text(.globalSection)) {
                if viewModel.payload.globalCompareItems.isEmpty {
                    Text(viewModel.text(.noGlobalItems))
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(viewModel.payload.globalCompareItems) { item in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.sourceName ?? "Source")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text(item.title).font(.headline)
                            if let summary = item.summary, !summary.isEmpty {
                                Text(summary).font(.callout)
                            }
                            Link(viewModel.text(.sourceOpen), destination: URL(string: item.url) ?? URL(string: "https://cxy2696.github.io/semiconductor/")!)
                                .font(.caption)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }

            Section("Sources") {
                ForEach(viewModel.payload.globalCompareRefs) { ref in
                    Link(ref.name, destination: URL(string: ref.url) ?? URL(string: "https://cxy2696.github.io/semiconductor/")!)
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(viewModel.text(.compareTitle))
        .refreshable {
            await viewModel.loadData(force: true)
        }
    }
}
