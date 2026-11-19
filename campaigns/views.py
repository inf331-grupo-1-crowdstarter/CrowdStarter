    return render(request, "campaigns/detail.html", _campaign_detail_context(campaign, contribution_form=form))


def _campaign_detail_context(campaign, *, comment_form=None, contribution_form=None):
    return {"campaign": campaign,
            "comments": campaign.comments.select_related("author"),
            "comment_form": comment_form if comment_form is not None else CommentForm(),
            "contribution_form": contribution_form if contribution_form is not None else ContributionForm()}


@login_required
@require_POST
def comment_create(request, pk):
    Campaign.expire_overdue()
    with transaction.atomic():
        # Match the contribution flow's SQLite locking before checking campaign status.
        Campaign.objects.filter(pk=pk).update(updated_at=F("updated_at"))
        campaign = get_object_or_404(Campaign.objects.select_for_update(), pk=pk)
        if campaign.status == Campaign.Status.BORRADOR and campaign.creator_id != request.user.pk:
            raise Http404
        if not campaign.accepts_comments:
            return HttpResponseForbidden("Esta campaña no acepta comentarios.")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.campaign = campaign
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentario publicado correctamente.")
            return redirect(campaign.get_absolute_url() + "#comentarios")
    return render(request, "campaigns/detail.html", _campaign_detail_context(campaign, comment_form=form))


@login_required
@require_POST
def comment_delete(request, pk, comment_pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.status == Campaign.Status.BORRADOR and campaign.creator_id != request.user.pk:
        raise Http404
    comment = get_object_or_404(Comment, pk=comment_pk, campaign=campaign, author=request.user)
    comment.delete()
    messages.success(request, "Comentario eliminado correctamente.")
    return redirect(campaign.get_absolute_url() + "#comentarios")


@login_required
def creator_panel(request):
    campaigns = Campaign.objects.filter(creator=request.user).order_by("-created_at")
    return render(request, "campaigns/creator_panel.html", {"campaigns": campaigns})