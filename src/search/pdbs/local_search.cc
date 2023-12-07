#include "local_search.h"

#include "pattern_generator.h"
#include "utils.h"

#include "../plugins/options.h"
#include "../plugins/plugin.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    LocalSearch::LocalSearch(const plugins::Options &opts) : PostHoc(opts),
                                                             iterations(opts.get<int>("n")),
                                                             op_order(opts.get<Order>("op_order")),
                                                             res_order(opts.get<Order>("res_order")),
                                                             decrement_mode(opts.get<Decrement>("decrement")),
                                                             seed(opts.get<int>("seed")),
                                                             use_ff(opts.get<bool>("ff")),
                                                             use_preferred(opts.get<bool>("preferred"))
    {
        if (use_ff)
        {
            hff = make_shared<ff_heuristic::FFHeuristic>(opts);
        }

        setup_restriction_ordering();
    }
    void LocalSearch::setup_restriction_ordering()
    {
        // restriction ordering index
        restriction_order.resize(restrictions.size());
        for (size_t i = 0; i < restrictions.size(); i++)
            restriction_order[i] = i;

        // sort restrictions by size
        if (res_order == Order::SORT)
        {
            std::stable_sort(restriction_order.begin(), restriction_order.end(),
                             [this](const int &a, const int &b)
                             {
                                 return restrictions[a].size() < restrictions[b].size();
                             });
        }

        // for each restriction, sort operators by mentions in restrictions
        if (op_order == Order::SORT)
        {
            for (int id_res : restriction_order)
            {
                std::stable_sort(restrictions[id_res].begin(), restrictions[id_res].end(),
                                 [this](const int &a, const int &b)
                                 {
                                     return restriction_operator[a].size() > restriction_operator[b].size();
                                 });
            }
        }
    }

    int LocalSearch::compute_heuristic(const State &ancestor_state)
    {
        int best = numeric_limits<int>::max();
        for (size_t i = 0; i < iterations; i++)
        {
            best = min(best, PostHoc::compute_heuristic(ancestor_state));
        }

        return best;
    }

    void LocalSearch::compute_post_hoc()
    {
        if (res_order == Order::RANDOM)
        {
            std::random_shuffle(restriction_order.begin(), restriction_order.end());
        }

        if (use_ff)
        {
            for (const int id_op : hff->get_preferred_operators(*state))
            {
                operator_count[id_op]++;
                for (size_t i = 0; i < restriction_operator[id_op].size(); i++)
                {
                    lower_bounds[restriction_operator[id_op][i]] -= operator_cost[id_op];
                }
            }
        }

        for (const int id_res : restriction_order)
        {

            if (decrement_mode == Decrement::BEFORE)
            {
                for (size_t i = 0; i < restrictions[id_res].size() && lower_bounds[id_res] > 0; i++)
                    lower_bounds[id_res] -= operator_cost[restrictions[id_res][i]] *
                                            operator_count[restrictions[id_res][i]];
            }

            if (op_order == Order::RANDOM)
            {
                std::random_shuffle(restrictions[id_res].begin(), restrictions[id_res].end());
            }

            int var = 0;
            while (lower_bounds[id_res] > 0)
            {
                const int id_op = restrictions[id_res][var];
                operator_count[id_op]++;

                if (decrement_mode == Decrement::ITERATIVE)
                {
                    for (size_t i = 0; i < restriction_operator[id_op].size(); i++)
                        lower_bounds[restriction_operator[id_op][i]] -= operator_cost[id_op];
                }

                if (decrement_mode == Decrement::BEFORE)
                {
                    lower_bounds[id_res] -= operator_cost[id_op];
                }

                var = (var + 1) % restrictions[id_res].size();
            }
        }

        if (use_preferred)
        {
            for (const OperatorProxy &op : task_proxy.get_operators())
            {
                if (operator_count[op.get_id()] > 0)
                    set_preferred(op);
            }
        }
    }

    class LocalSearchFeature : public PostHocFeature<LocalSearch>
    {
    public:
        LocalSearchFeature() : PostHocFeature<LocalSearch>("lsh", "LocalSearch heuristic")
        {
            Feature::add_option<int>(
                "n",
                "number of iterations of randomized order",
                "1",
                plugins::Bounds("1", "1000"));

            Feature::add_option<Order>("res_order",
                                       "Restriction order",
                                       "default");

            Feature::add_option<Order>("op_order",
                                       "Operator order",
                                       "default");

            Feature::add_option<Decrement>("decrement",
                                           "Decrement mode",
                                           "iterative");

            Feature::add_option<bool>(
                "ff",
                "",
                "false");

            Feature::add_option<bool>(
                "preferred",
                "set preferred opeartors",
                "false");

            document_language_support("action costs", "supported");
            document_language_support("conditional effects", "not supported");
            document_language_support("axioms", "not supported");
            document_property("admissible", "no");
            document_property("consistent", "no");
            document_property("safe", "yes");
            document_property("preferred operators", "no");
        }
    };
    static plugins::FeaturePlugin<LocalSearchFeature> _plugin;
    static plugins::TypedEnumPlugin<Order> _enum_order_plugin({{"sort", "sort"}, {"random", "random"}, {"default", "default"}});
    static plugins::TypedEnumPlugin<Decrement> _enum_decrement_plugin({{"before", "before"}, {"iterative", "iterative"}});
}
