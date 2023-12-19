#include "improved_local_search.h"

#include "utils.h"

#include "../plugins/plugin.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    ImprovedLocalSearch::ImprovedLocalSearch(const plugins::Options &opts) : PostHoc(opts)
    {
    }

    void ImprovedLocalSearch::compute_post_hoc()
    {
        while (is_any_restriction_lower_bound_greater_than_zero())
        {
            int operator_id = get_best_operator();

            int times_to_increment = compute_times_to_increment(operator_id);
            operator_count[operator_id] += times_to_increment;

            for (const int restriction_id : restriction_operator[operator_id])
                lower_bounds[restriction_id] -= operator_cost[operator_id];
        }
    }

    float ImprovedLocalSearch::compute_operator_performance(const int operator_id)
    {
        float sum = 0;
        const int operator_cost = this->operator_cost[operator_id];

        for (size_t i = 0; i < this->restriction_operator[operator_id].size(); i++)
        {
            sum += std::min(1, this->lower_bounds[i] / operator_cost);
        }

        return sum;
    }

    int ImprovedLocalSearch::get_best_operator()
    {
        int best_operator_id = -1;
        float best_operator_performance = -1;

        for (size_t i = 0; i < this->operators.size(); i++)
        {
            int operator_id = this->operators[i];
            float operator_performance = this->compute_operator_performance(operator_id);

            if (best_operator_id == -1 || best_operator_performance < operator_performance)
            {
                best_operator_id = operator_id;
                best_operator_performance = operator_performance;

                continue;
            }
        }

        return best_operator_id;
    }

    int ImprovedLocalSearch::compute_times_to_increment(const int operator_id)
    {
        int minimum_lower_bound = -1;
        int operator_cost = this->operator_cost[operator_id];

        for (size_t i = 0; i < this->restriction_operator[operator_id].size(); i++)
        {
            if (minimum_lower_bound < this->lower_bounds[i])
            {
                minimum_lower_bound = this->lower_bounds[i];
            }
        }

        return std::max(1, minimum_lower_bound / operator_cost);
    }

    bool ImprovedLocalSearch::is_any_restriction_lower_bound_greater_than_zero()
    {
        for (int lower_bound : lower_bounds)
        {
            if (lower_bound > 0)
                return true;
        }

        return false;
    }

    class ImprovedLocalSearchFeature : public PostHocFeature<ImprovedLocalSearch>
    {
    public:
        ImprovedLocalSearchFeature() : PostHocFeature<ImprovedLocalSearch>("ilsh", "ImprovedLocalSearch heuristic")
        {
            document_language_support("action costs", "supported");
            document_language_support("conditional effects", "not supported");
            document_language_support("axioms", "not supported");
            document_property("admissible", "no");
            document_property("consistent", "no");
            document_property("safe", "yes");
            document_property("preferred operators", "no");
        }
    };
    static plugins::FeaturePlugin<ImprovedLocalSearchFeature> _plugin;
}
