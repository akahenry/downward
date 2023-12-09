#ifndef POST_HOC_HEURISTIC_H
#define POST_HOC_HEURISTIC_H

#include "pattern_database.h"
#include "pattern_generator.h"

#include "../heuristic.h"

#include "types.h"
#include "../plugins/options.h"
#include "../plugins/plugin.h"

namespace pdbs
{

    class PostHoc : public Heuristic
    {
    protected:
        std::shared_ptr<PDBCollection> pdbs;
        State *state;

        std::vector<int> operators;
        std::vector<int> operator_cost;
        std::vector<int> operator_count;

        std::vector<std::vector<int>> restrictions;
        std::vector<std::vector<int>> restriction_operator;

        std::vector<int> value_pdbs;
        std::vector<int> lower_bounds;

        virtual int compute_heuristic(const State &ancestor_state) override;

        virtual void compute_post_hoc() = 0;

        int set_value_pdbs(const State &state);

        void get_restrictions();

        void print_info();

    private:
        int seed;

    public:
        explicit PostHoc(const plugins::Options &opts);
        virtual ~PostHoc() = default;
    };

    template <typename T>
    class PostHocFeature : public plugins::TypedFeature<Evaluator, T>
    {
    public:
        PostHocFeature(const std::string key,
                       const std::string title,
                       const std::string pattern_generation_method = "systematic(4)") : plugins::TypedFeature<Evaluator, T>(key)
        {
            this->document_title(title);

            this->template add_option<std::shared_ptr<PatternCollectionGenerator>>("patterns",
                                                                                   "pattern generation method",
                                                                                   pattern_generation_method);

            this->template add_option<int>("seed",
                                           "random seed",
                                           "0",
                                           plugins::Bounds("0", "2147483646"));

            Heuristic::add_options_to_feature(*this);
        }
    };
}

#endif
