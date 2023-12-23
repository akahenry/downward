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

    ImprovedLocalSearch::ImprovedLocalSearch(const plugins::Options &opts) : PostHoc(opts),
                                                                             tie_breaking_operation(opts.get<TieBreakingOperation>("tie_breaking"))

    {
        utils::g_log << "Tie breaking: " << this->tie_breaking_operation << endl;
    }

    void ImprovedLocalSearch::compute_post_hoc()
    {
        this->update_operators_with_simple_restrictions();

        while (is_any_restriction_lower_bound_greater_than_zero())
        {
            int operator_id = get_best_operator();

            int times_to_increment = compute_times_to_increment(operator_id);
            operator_count[operator_id] += times_to_increment;

            update_lower_bounds_with_selected_operator(operator_id, times_to_increment);
        }
    }

    void ImprovedLocalSearch::update_lower_bounds_with_selected_operator(int operator_id, int times_to_increment)
    {
        for (const int restriction_id : restriction_operator[operator_id])
            lower_bounds[restriction_id] -= times_to_increment * operator_cost[operator_id];
    }

    float ImprovedLocalSearch::compute_operator_performance(const int operator_id)
    {
        float sum = 0;
        const int operator_cost = this->operator_cost[operator_id];

        for (size_t i = 0; i < this->restriction_operator[operator_id].size(); i++)
        {
            sum += std::min(1.0f, (float)this->lower_bounds[this->restriction_operator[operator_id][i]] / operator_cost);
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

            if (best_operator_performance == operator_performance)
            {
                best_operator_id = this->compute_operator_tie_breaking(best_operator_id, operator_id);
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

    void ImprovedLocalSearch::update_operators_with_simple_restrictions()
    {
        for (size_t i = 0; i < this->restrictions.size(); i++)
        {
            if (this->restrictions[i].size() == 1)
            {
                int operator_id = this->restrictions[i][0];
                int times_to_increment = (int)std::ceil((float)this->lower_bounds[i] / this->operator_cost[operator_id]);
                this->operator_count[operator_id] = std::max(this->operator_count[operator_id], times_to_increment);
            }
        }

        for (size_t i = 0; i < this->operators.size(); i++)
        {
            this->update_lower_bounds_with_selected_operator(this->operators[i], this->operator_count[i]);
        }
    }

    int ImprovedLocalSearch::compute_operator_tie_breaking(int operator_id_a, int operator_id_b)
    {
        switch (this->tie_breaking_operation)
        {
        case TieBreakingOperation::MAX_CONSTRAINT:
            return this->compute_tie_breaking_max_constraint(operator_id_a, operator_id_b);
        case TieBreakingOperation::SUM_CONSTRAINTS:
            return this->compute_tie_breaking_sum_constraint(operator_id_a, operator_id_b);
        case TieBreakingOperation::SUM_SQUARE_CONSTRAINTS:
            return this->compute_tie_breaking_sum_square_constraint(operator_id_a, operator_id_b);
        }

        throw std::runtime_error("TieBreakingOperation not found");
    }

    int ImprovedLocalSearch::compute_tie_breaking_max_constraint(int operator_id_a, int operator_id_b)
    {
        return this->compute_tie_breaking_lambda_for_operators(operator_id_a, operator_id_b, [](std::vector<int> list)
                                                               { 
                                                                int max = 0;
                                                                for (const int n : list) {
                                                                    max = std::max(max, n);
                                                                }
                                                                return max; });
    }

    int ImprovedLocalSearch::compute_tie_breaking_sum_constraint(int operator_id_a, int operator_id_b)
    {
        return this->compute_tie_breaking_lambda_for_operators(operator_id_a, operator_id_b, [](std::vector<int> list)
                                                               { return std::accumulate(list.begin(), list.end(), 0); });
    }

    int ImprovedLocalSearch::compute_tie_breaking_sum_square_constraint(int operator_id_a, int operator_id_b)
    {
        return this->compute_tie_breaking_lambda_for_operators(operator_id_a, operator_id_b, [](std::vector<int> list)
                                                               { 
                                                                int acc = 0;
                                                                for (const int n : list) {
                                                                    acc += (int)std::pow(n, 2);
                                                                }
                                                                return acc; });
    }

    int ImprovedLocalSearch::compute_tie_breaking_lambda_for_operators(int operator_id_a, int operator_id_b, std::function<int(std::vector<int>)> lambda)
    {
        int a_value = this->get_lambda_constraint_value_for_operator(operator_id_a, lambda);
        int b_value = this->get_lambda_constraint_value_for_operator(operator_id_b, lambda);

        return a_value < b_value ? operator_id_b : operator_id_a;
    }

    int ImprovedLocalSearch::get_lambda_constraint_value_for_operator(int operator_id, std::function<int(std::vector<int>)> lambda)
    {
        std::vector<int> restrictions_lower_bounds;

        for (const int restriction : this->restriction_operator[operator_id])
        {
            restrictions_lower_bounds.push_back(this->lower_bounds[restriction]);
        }

        return lambda(restrictions_lower_bounds);
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
            Feature::add_option<TieBreakingOperation>("tie_breaking",
                                                      "Operation to use for tie breaking when selecting best operator",
                                                      "sum_square_constraints");

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
    static plugins::TypedEnumPlugin<TieBreakingOperation> _enum_tie_breaking_plugin({{"max_constraint", "max_constraint"}, {"sum_constraints", "sum_constraints"}, {"sum_square_constraints", "sum_square_constraints"}});
}
