<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer app clipped right width="800">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title class="title">
              {{ name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              Reported - {{ reported_at | formatRelativeDate }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-spacer />
          <v-btn
            icon
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeEditSheet">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs color="primary" fixed-tabs v-model="tab">
        <v-tab key="details"> Details </v-tab>
        <v-tab key="resources"> Resources </v-tab>
        <v-tab key="participants"> Participants </v-tab>
        <v-tab key="timeline"> Timeline </v-tab>
        <v-tab key="tasks"> Tasks </v-tab>
        <v-tab key="workflows"> Workflows </v-tab>
        <v-tab key="costs"> Costs </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item key="details">
          <incident-details-tab />
        </v-tab-item>
        <v-tab-item key="resources">
          <incident-resources-tab />
        </v-tab-item>
        <v-tab-item key="participants">
          <incident-participants-tab />
        </v-tab-item>
        <v-tab-item key="timeline">
          <incident-timeline-tab />
        </v-tab-item>
        <v-tab-item key="tasks">
          <incident-tasks-tab />
        </v-tab-item>
        <v-tab-item key="workflow_instances">
          <workflow-instance-tab v-model="workflow_instances" />
        </v-tab-item>
        <v-tab-item key="costs">
          <incident-costs-tab />
        </v-tab-item>
      </v-tabs-items>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

import IncidentCostsTab from "@/incident/CostsTab.vue"
import IncidentDetailsTab from "@/incident/DetailsTab.vue"
import IncidentParticipantsTab from "@/incident/ParticipantsTab.vue"
import IncidentResourcesTab from "@/incident/ResourcesTab.vue"
import IncidentTasksTab from "@/incident/TasksTab.vue"
import IncidentTimelineTab from "@/incident/TimelineTab.vue"
import WorkflowInstanceTab from "@/workflow/WorkflowInstanceTab.vue"

export default {
  name: "IncidentEditSheet",

  components: {
    IncidentCostsTab,
    IncidentDetailsTab,
    IncidentParticipantsTab,
    IncidentResourcesTab,
    IncidentTasksTab,
    IncidentTimelineTab,
    ValidationObserver,
    WorkflowInstanceTab,
  },

  data() {
    return {
      tab: null,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.reported_at",
      "selected.loading",
      "selected.workflow_instances",
      "dialogs.showEditSheet",
    ]),
  },

  created() {
    this.fetchDetails()
  },

  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
  },

  methods: {
    fetchDetails() {
      this.getDetails({ name: this.$route.params.name })
    },
    ...mapActions("incident", ["save", "getDetails", "closeEditSheet"]),
  },
}
</script>
