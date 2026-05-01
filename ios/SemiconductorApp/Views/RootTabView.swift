import SwiftUI

struct RootTabView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        TabView {
            NavigationStack {
                HomeView()
            }
            .tabItem {
                Label(viewModel.text(.homeTitle), systemImage: "house")
            }

            NavigationStack {
                CompareView()
            }
            .tabItem {
                Label(viewModel.text(.compareTitle), systemImage: "globe")
            }

            NavigationStack {
                MarketView()
            }
            .tabItem {
                Label(viewModel.text(.marketTitle), systemImage: "list.bullet.rectangle")
            }

            NavigationStack {
                NewsView()
            }
            .tabItem {
                Label(viewModel.text(.newsTitle), systemImage: "newspaper")
            }

            NavigationStack {
                SettingsView()
            }
            .tabItem {
                Label(viewModel.text(.settingsTitle), systemImage: "gearshape")
            }
        }
        .tint(.blue)
        .overlay(alignment: .bottom) {
            if viewModel.isLoading {
                HStack(spacing: 8) {
                    ProgressView()
                    Text(viewModel.text(.loading))
                        .font(.footnote)
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(.thinMaterial, in: Capsule())
                .padding(.bottom, 12)
            }
        }
    }
}
