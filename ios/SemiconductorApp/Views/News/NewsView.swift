import SwiftUI

struct NewsView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        List(viewModel.payload.newsPool) { item in
            VStack(alignment: .leading, spacing: 6) {
                Text(item.date).font(.caption).foregroundStyle(.secondary)
                Text(item.title).font(.headline)
                Link(viewModel.text(.sourceOpen), destination: URL(string: item.link) ?? URL(string: "https://cxy2696.github.io/semiconductor/")!)
                    .font(.caption)
            }
            .padding(.vertical, 4)
        }
        .navigationTitle(viewModel.text(.newsTitle))
        .refreshable {
            await viewModel.loadData(force: true)
        }
    }
}
