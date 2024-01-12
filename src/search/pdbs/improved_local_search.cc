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
        this->init_internal_attributes();
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
        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            this->lower_bounds[restriction_id] -= times_to_increment * operator_cost[operator_id];
            this->lower_bounds_squared[restriction_id] = this->lower_bounds[restriction_id] * this->lower_bounds[restriction_id];
            if (this->lower_bounds[restriction_id] <= 0)
            {
                this->delete_restriction(restriction_id);
            }
        }
    }

    float ImprovedLocalSearch::compute_operator_performance(const int operator_id)
    {
        int sum = 0;
        const int operator_cost = this->operator_cost[operator_id];

        // TODO: we may want to change `relevante_restrictions_by_operator` to std::vector<std::unordered_set<int>> to consider only valid restrictions
        // or use a different logic to iterate only over valid restrictions (e.g. swap satisfied restriction on the delete method)
        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            sum += std::min(operator_cost, this->lower_bounds[restriction_id]);
        }

        return (float)sum / operator_cost;
    }

    int ImprovedLocalSearch::get_best_operator()
    {
        int best_operator_id = -1;
        float best_operator_performance = -1;
        int best_operator_tie_breaking = INT_MIN;

        for (const int &operator_id : this->operators)
        {
            float operator_performance = this->compute_operator_performance(operator_id);

            if (best_operator_performance < operator_performance || best_operator_id == -1)
            {
                best_operator_id = operator_id;
                best_operator_performance = operator_performance;
                best_operator_tie_breaking = INT_MIN;

                continue;
            }

            if (best_operator_performance == operator_performance)
            {
                if (best_operator_tie_breaking == INT_MIN)
                {
                    best_operator_tie_breaking = this->compute_operator_tie_breaking(best_operator_id);
                }

                int operator_tie_breaking = this->compute_operator_tie_breaking(operator_id);
                if (best_operator_tie_breaking < operator_tie_breaking)
                {
                    best_operator_id = operator_id;
                    best_operator_tie_breaking = operator_tie_breaking;
                }
            }
        }

        return best_operator_id;
    }

    int ImprovedLocalSearch::compute_times_to_increment(const int operator_id)
    {
        int minimum_lower_bound = INT_MAX;
        int operator_cost = this->operator_cost[operator_id];

        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            if (minimum_lower_bound > this->lower_bounds[restriction_id])
            {
                minimum_lower_bound = this->lower_bounds[restriction_id];
                if (minimum_lower_bound <= operator_cost)
                {
                    break;
                }
            }
        }

        return std::max(1, minimum_lower_bound / operator_cost);
    }

    void ImprovedLocalSearch::update_operators_with_simple_restrictions()
    {
        std::vector<int> operators_to_update;
        for (const int &restriction_id : this->simple_restrictions_ids)
        {
            int operator_id = *this->relevant_operators_by_restriction[restriction_id].begin();

            // The code below does the same as the following commented code but in a faster way
            // int times_to_increment = (int)std::ceil((float)this->lower_bounds[restriction_id] / this->operator_cost[operator_id]);
            int times_to_increment = (this->lower_bounds[restriction_id] + this->operator_cost[operator_id] - 1) / this->operator_cost[operator_id];

            if (this->operator_count[operator_id] == 0)
            {
                operators_to_update.push_back(operator_id);
            }
            this->operator_count[operator_id] = std::max(this->operator_count[operator_id], times_to_increment);
        }

        for (const int &operator_id : operators_to_update)
        {
            this->update_lower_bounds_with_selected_operator(operator_id, this->operator_count[operator_id]);
        }
    }

    int ImprovedLocalSearch::compute_operator_tie_breaking(const int operator_id)
    {
        switch (this->tie_breaking_operation)
        {
        case TieBreakingOperation::MAX_CONSTRAINT:
            return this->compute_tie_breaking_max_constraint(operator_id);
        case TieBreakingOperation::SUM_CONSTRAINTS:
            return this->compute_tie_breaking_sum_constraint(operator_id);
        case TieBreakingOperation::SUM_SQUARE_CONSTRAINTS:
            return this->compute_tie_breaking_sum_square_constraint(operator_id);
        }

        throw std::runtime_error("TieBreakingOperation not found");
    }

    int ImprovedLocalSearch::compute_tie_breaking_max_constraint(const int operator_id)
    {
        int acc = 0;
        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            acc = std::max(acc, this->lower_bounds[restriction_id]);
        }
        return acc;
    }

    int ImprovedLocalSearch::compute_tie_breaking_sum_constraint(const int operator_id)
    {
        int acc = 0;
        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            acc += this->lower_bounds[restriction_id];
        }
        return acc;
    }

    int ImprovedLocalSearch::compute_tie_breaking_sum_square_constraint(const int operator_id)
    {
        int acc = 0;
        for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
        {
            if (this->is_restriction_deleted(restriction_id))
            {
                continue;
            }

            acc += this->lower_bounds_squared[restriction_id];
        }
        return acc;
    }

    void ImprovedLocalSearch::delete_restriction(int restriction_id)
    {
        this->restrictions_valid[restriction_id] = false;
        restrictions_with_lower_bound_greater_than_zero--;
    }

    inline bool ImprovedLocalSearch::is_restriction_deleted(int restriction_id)
    {
        return !this->restrictions_valid[restriction_id];
    }

    void ImprovedLocalSearch::init_internal_attributes()
    {
        this->restrictions_valid.assign(this->relevant_operators_by_restriction.size(), true);
        this->restrictions_with_lower_bound_greater_than_zero = this->relevant_operators_by_restriction.size();
        this->lower_bounds_squared.resize(this->restrictions_valid.size(), 0);
        for (size_t restriction_id = 0; restriction_id < this->relevant_operators_by_restriction.size(); restriction_id++)
        {
            this->lower_bounds_squared[restriction_id] = this->lower_bounds[restriction_id] * this->lower_bounds[restriction_id];
            if (this->lower_bounds[restriction_id] <= 0)
            {
                this->delete_restriction(restriction_id);
            }
        }
    }

    inline bool ImprovedLocalSearch::is_any_restriction_lower_bound_greater_than_zero()
    {
        return this->restrictions_with_lower_bound_greater_than_zero > 0;
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
