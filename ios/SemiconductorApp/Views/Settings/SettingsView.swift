import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        Form {
            Section(viewModel.text(.localeTime)) {
                Picker(viewModel.text(.profile), selection: $viewModel.localeProfile) {
                    ForEach(DashboardViewModel.LocaleProfile.allCases) { profile in
                        Text(profile.title).tag(profile)
                    }
                }
                .pickerStyle(.inline)
            }

            Section(viewModel.text(.dataSection)) {
                Button(viewModel.text(.refreshNow)) {
                    Task {
                        await viewModel.loadData(force: true)
                    }
                }
                if let err = viewModel.errorMessage, !err.isEmpty {
                    Text(err)
                        .font(.footnote)
                        .foregroundStyle(.red)
                }
            }
        }
        .navigationTitle(viewModel.text(.settingsTitle))
    }
}
