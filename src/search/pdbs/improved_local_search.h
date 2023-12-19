#ifndef IMPROVED_LOCAL_SEARCH_HEURISTIC_H
#define IMPROVED_LOCAL_SEARCH_HEURISTIC_H

#include "pattern_database.h"

#include "../heuristic.h"
#include "post_hoc.h"

#include "types.h"
#include "../plugins/options.h"

namespace pdbs
{
    class ImprovedLocalSearch : public PostHoc
    {
        float compute_operator_performance(const int operator_id);
        int get_best_operator();
        int compute_times_to_increment(const int operator_id);
        bool is_any_restriction_lower_bound_greater_than_zero();
        void update_lower_bounds_with_selected_operator(int operator_id, int times_to_increment);
        void update_operators_with_simple_restrictions();

    protected:
        void compute_post_hoc() override;

    public:
        explicit ImprovedLocalSearch(const plugins::Options &opts);
        virtual ~ImprovedLocalSearch() = default;
    };
}

#endif
